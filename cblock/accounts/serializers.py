import logging

from django.utils.translation import ugettext_lazy as _

from rest_auth.registration.serializers import SocialLoginSerializer, RegisterSerializer
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from cblock.accounts.models import Profile
from cblock.accounts.utils import valid_metamask_message
from web3 import Web3


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
            metamask_user = User.objects.filter(username__iexact=address).first()

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

class MetamaskUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['email', 'owner_address']
        read_only_fields = fields

def email_address_exists(email, exclude_user=None):
    from .account import app_settings as account_settings
    from .account.models import EmailAddress

    emailaddresses = EmailAddress.objects
    if exclude_user:
        emailaddresses = emailaddresses.exclude(user=exclude_user)
    ret = emailaddresses.filter(email__iexact=email).exists()
    if not ret:
        email_field = account_settings.USER_MODEL_EMAIL_FIELD
        if email_field:
            users = get_user_model().objects
            if exclude_user:
                users = users.exclude(pk=exclude_user.pk)
            ret = users.filter(**{email_field + "__iexact": email}).exists()
    return


class MetamaskRegisterSerializer(RegisterSerializer):
    username = None
    owner_address = serializers.CharField(required=True, allow_blank=False)
    message = serializers.CharField(required=True, allow_blank=False)
    signature = serializers.CharField(required=True, allow_blank=False)

    @staticmethod
    def get_owner_address_exists(owner_address):
        return Profile.objects.filter(owner_address__iexact=owner_address).exists()

    @staticmethod
    def get_email_and_address_exists(email, owner_address):
        return Profile.objects.filter(email__iexact=email, owner_address__iexact=owner_address).exists()


    def validate(self, data):
        super(MetamaskRegisterSerializer, self).validate(data)

        data['owner_address'] = data['owner_address'].lower()

        if not valid_metamask_message(data.get('owner_address'), data.get('message'), data.get('signature')):
            raise serializers.ValidationError(_("Provided signature is not correct"))

        if data.get('owner_address') and self.get_owner_address_exists(data.get('owner_address')):
            raise serializers.ValidationError(_("A user is already registered with this metamask address."))

        if self.get_email_and_address_exists(data.get('email'), data.get('owner_address')):
            raise serializers.ValidationError(_("Pair of this user address and email already exists"))

        return data


    def get_cleaned_data(self):
        super(MetamaskRegisterSerializer, self).get_cleaned_data()
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'owner_address': self.validated_data.get('owner_address', '')
        }

    def save(self, request):
        user = super().save(request)
        user.owner_address = self.get_cleaned_data().get('owner_address')
        user.save()
        return user

