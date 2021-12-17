from rest_framework import serializers
from .models import TokenContract, ProbateContract, WeddingContract, CrowdsaleContract


class ProbateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProbateContract
        fields = ('address', 'mails_array', 'owner_mail')


class ProbateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProbateContract
        extra_kwargs = {
            'test_node': {'read_only': True}
        }
        fields = ('address', 'name', 'mails_array', 'owner', 'owner_mail')

    def create(self, validated_data):
        return ProbateContract.objects.update_or_create(**validated_data)


class CrowdsaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrowdsaleContract
        extra_kwargs = {
            'test_node': {'read_only': True}
        }
        fields = ('address', 'name', 'owner')

    def create(self, validated_data):
        return CrowdsaleContract.objects.update_or_create(**validated_data)


class WeddingSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeddingContract
        extra_kwargs = {
            'test_node': {'only_read': True}
        }
        fields = ('address', 'name', 'mail_list', 'owner')

    def create(self, validated_data):
        return WeddingContract.objects.update_or_create(**validated_data)


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = TokenContract
        extra_kwargs = {
            'contract_type': {'read_only': True},
            'test_node': {'read_only': True}
        }
        fields = ('address', 'address_list', 'contract_type', 'name', 'owner')

    def create(self, validated_data):
        return TokenContract.objects.update_or_create(**validated_data)


class HistoryResponseSerializer(serializers.Serializer):
    tokens = TokenSerializer()
    probates = ProbateSerializer()
    crowdsales = CrowdsaleSerializer()
    weddings = WeddingSerializer()
