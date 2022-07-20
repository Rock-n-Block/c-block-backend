import logging
from urllib.parse import urlparse
from web3 import Web3
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext_lazy as _

from rest_auth.registration.serializers import SocialLoginSerializer, RegisterSerializer
from rest_auth.serializers import PasswordResetSerializer
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django_countries.serializers import CountryFieldMixin

from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from cblock.settings import DEFAULT_FROM_EMAIL
from cblock.accounts.models import Profile
from cblock.accounts.utils import valid_metamask_message, get_domain_for_emails


class MetamaskLoginSerializer(SocialLoginSerializer):
    address = serializers.CharField(required=False, allow_blank=True)
    msg = serializers.CharField(required=False, allow_blank=True)
    signed_msg = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        address = Web3.toChecksumAddress(attrs['address'])
        signature = attrs['signed_msg']
        session = self.context['request'].session
        message = session.get('metamask_message')

        if message is None:
            message = attrs['msg']

        print('metamask login, address', address, 'message', message, 'signature', signature, flush=True)
        if valid_metamask_message(address, message, signature):
            metamask_user = Profile.objects.filter(username__iexact=address).first()

            if metamask_user is None:
                self.user = Profile.objects.create(username=address)
            else:
                self.user = metamask_user

            attrs['user'] = self.user

            if not self.user.is_active:
                raise PermissionDenied(1035)

        else:
            raise PermissionDenied(1034)

        return attrs

class MetamaskUserSerializer(CountryFieldMixin, serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'owner_address', 'name', 'company', 'phone_number',
            'country', 'city', 'street', 'office', 'building', 'zipcode',
            'avatar', 'freezed', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'owner_address', 'freezed', 'date_joined']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['is_completed_profile'] = instance.is_completed_profile()
        rep['permissions'] = instance.get_role_system_permissions()
        if rep['avatar']:
            rep['avatar'] = urlparse(rep['avatar']).path

        return rep


class MetamaskRegisterSerializer(RegisterSerializer):
    username = None
    owner_address = serializers.CharField(required=True, allow_blank=False)
    message = serializers.CharField(required=True, allow_blank=False)
    signature = serializers.CharField(required=True, allow_blank=False)

    @staticmethod
    def get_owner_address_exists(owner_address):
        return Profile.objects.filter(owner_address__iexact=owner_address.lower()).exists()

    @staticmethod
    def get_email_and_address_exists(email, owner_address):
        return Profile.objects.filter(email__iexact=email, owner_address__iexact=owner_address.lower()).exists()


    def validate(self, data):
        data['owner_address'] = data['owner_address'].lower()

        if not valid_metamask_message(data.get('owner_address'), data.get('message'), data.get('signature')):
            raise serializers.ValidationError(_("Provided signature is not correct"))

        if data.get('owner_address') and self.get_owner_address_exists(data.get('owner_address')):
            raise serializers.ValidationError(_("A user is already registered with this metamask address."))

        if self.get_email_and_address_exists(data.get('email'), data.get('owner_address')):
            raise serializers.ValidationError(_("Pair of this user address and email already exists"))

        data = super(MetamaskRegisterSerializer, self).validate(data)

        return data



    def get_cleaned_data(self):
        # super(MetamaskRegisterSerializer, self).get_cleaned_data()
        # logging.info(self.validated_data)
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'owner_address': self.validated_data.get('owner_address', '')
        }

    # def save(self, request):
    #     user = super().save(request)
    #     user.owner_address = self.get_cleaned_data().get('owner_address')
    #     user.save()
    #     return user
    #
    # def save(self, request):
    #     adapter = get_adapter()
    #     user = adapter.new_user(request)
    #     self.cleaned_data = self.get_cleaned_data()
    #     logging.info(self.cleaned_data)
    #     adapter.save_user(request, user, self)
    #     self.custom_signup(request, user)
    #     setup_user_email(request, user, [])
    #     return user


class CustomDomainPasswordResetSerializer(PasswordResetSerializer):
    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'domain_override': get_domain_for_emails(request),
            'use_https': request.is_secure(),
            'from_email': DEFAULT_FROM_EMAIL,
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)