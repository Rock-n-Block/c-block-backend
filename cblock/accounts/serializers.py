import logging

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


class MetamaskRegisterSerializer(RegisterSerializer):
    username = None
    owner_address = serializers.CharField(required=True, allow_blank=False)
    message = serializers.CharField(required=True, allow_blank=False)
    signature = serializers.CharField(required=True, allow_blank=False)

    def validate(self, data):
        super(MetamaskRegisterSerializer, self).validate(data)
        if not valid_metamask_message(data.get('owner_address'), data.get('message'), data.get('signature')):
            raise serializers.ValidationError("Provided signature is not correct")
        return data


    def get_cleaned_data(self):
        super(MetamaskRegisterSerializer, self).get_cleaned_data()
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'owner_address': self.validated_data.get('owner_address', '')
        }

