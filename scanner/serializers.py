from rest_framework import serializers
from .models import TokenContract, ProbateContract, WeddingContract, CrowdsaleContract, Profile


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenContract
        fields = ('address', 'address_list', 'contract_type', 'test_node')


class ProbateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProbateContract
        fields = ('address', 'name', 'mails_array', 'owner_mail', 'test_node')


class CrowdsaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrowdsaleContract
        fields = ('address', 'name', 'test_node')


class WeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeddingContract
        fields = ('address', 'name', 'mail_list', 'test_node')


class ResponseSerializer(serializers.Serializer):
    token = TokenSerializer()
    probate = ProbateSerializer()
    crowdsale = CrowdsaleSerializer()
    wedding = WeddingSerializer()


class ProbateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProbateContract
        fields = ('address', 'mails_array', 'owner_mail')


class ProbateCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProbateContract
        fields = ('address', 'name', 'mails_array', 'owner', 'owner_mail')

    def create(self, validated_data):
        return ProbateContract.objects.update_or_create(**validated_data)


class CrowdsaleCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrowdsaleContract
        fields = ('address', 'name', 'owner')

    def create(self, validated_data):
        return CrowdsaleContract.objects.update_or_create(**validated_data)


class WeddingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeddingContract
        fields = ('address', 'name', 'mail_list', 'owner')

    def create(self, validated_data):
        return WeddingContract.objects.update_or_create(**validated_data)


class TokenCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TokenContract
        fields = ('address', 'address_list', 'name', 'owner')

    def create(self, validated_data):
        return TokenContract.objects.update_or_create(**validated_data)
