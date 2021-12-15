from rest_framework import serializers
from .models import TokenContract, ProbateContract, WeddingContract, CrowdsaleContract


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
