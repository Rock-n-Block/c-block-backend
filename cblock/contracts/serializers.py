from rest_framework import serializers


from cblock.contracts.models import TokenContract, LastWillContract, LostKeyContract, WeddingContract, CrowdsaleContract

import logging

logger = logging.getLogger(__name__)


class ProbateListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('address', 'owner_mail', 'is_testnet')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        probate_mails = {}
        logger.info(instance)
        for mail_address in instance.mails.all():
            probate_mails[mail_address.email] = mail_address.address.lower()

        representation['mails'] = probate_mails
        return representation


class LastWillListSerializer(ProbateListSerializer):
    class Meta(ProbateListSerializer.Meta):
        model = LastWillContract


class LostKeyListSerializer(ProbateListSerializer):
    class Meta(ProbateListSerializer.Meta):
        model = LostKeyContract


class ProbateSerializer(serializers.ModelSerializer):

    class Meta:
        extra_kwargs = {
            # 'is_testnet': {'read_only': True},
            'address': {'read_only': True},
            'mails': {'read_only': True},
        }
            
        fields = ('address', 'tx_hash', 'name', 'owner_mail', 'is_testnet')

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        probate_mails = {}
        logger.info(instance)
        for mail_address in instance.mails.all():
            probate_mails[mail_address.email] = mail_address.address.lower()

        representation['mails'] = probate_mails
        return representation


class LastWillSerializer(ProbateSerializer):
    class Meta(ProbateSerializer.Meta):
        model = LastWillContract

    def create(self, validated_data):
        return LastWillContract.objects.create(**validated_data)


class LostKeySerializer(ProbateSerializer):
    class Meta(ProbateSerializer.Meta):
        model = LostKeyContract

    def create(self, validated_data):
        return LostKeyContract.objects.create(**validated_data)


class CrowdsaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrowdsaleContract
        extra_kwargs = {
            # 'is_testnet': {'read_only': True},
            'address': {'read_only': True},
        }
        fields = ('address', 'tx_hash', 'name', 'is_testnet')

    def create(self, validated_data):
        return CrowdsaleContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class WeddingSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeddingContract
        extra_kwargs = {
            # 'is_testnet': {'read_only': True},
            'address': {'read_only': True},
            'mails':  {'read_only': True},
        }
        fields = ('address', 'tx_hash', 'name', 'is_testnet')

    def create(self, validated_data):
        return WeddingContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        wedding_mails = {}
        logger.info(instance)
        for mail_address in instance.mails.all():
            wedding_mails[mail_address.email] = mail_address.address.lower()

        representation['mails'] = wedding_mails
        return representation


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = TokenContract
        extra_kwargs = {
            'contract_type': {'read_only': True},
            # 'is_testnet': {'read_only': True},
            'address': {'read_only': True},
            'addresses': {'read_only': False},
        }
        fields = ('address', 'tx_hash', 'name',  'contract_type', 'is_testnet')

    def create(self, validated_data):
        return TokenContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        token_holders = {}
        logger.info(instance)
        for token_holder in instance.addresses.all():
            token_holders[token_holder.name] = token_holder.address.lower()

        representation['addresses'] = token_holders
        return representation


class HistoryResponseSerializer(serializers.Serializer):
    tokens = TokenSerializer()
    lastwills = LastWillSerializer()
    lostkeys = LostKeySerializer()
    crowdsales = CrowdsaleSerializer()
    weddings = WeddingSerializer()
