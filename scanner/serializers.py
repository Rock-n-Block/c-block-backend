from rest_framework import serializers

from .models import TokenContract, ProbateContract, WeddingContract, CrowdsaleContract


class ProbateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProbateContract
        fields = ('address', 'mails', 'owner_mail')


class ProbateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProbateContract
        extra_kwargs = {
            'test_node': {'read_only': True},
            'address': {'read_only': True}
        }
            
        fields = ('address', 'tx_hash', 'name', 'mails', 'owner_mail', 'test_node')

    def create(self, validated_data):
        return ProbateContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CrowdsaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrowdsaleContract
        extra_kwargs = {
            'test_node': {'read_only': True},
            'address': {'read_only': True},
        }
        fields = ('address', 'tx_hash', 'name', 'test_node')

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
            'test_node': {'read_only': True},
            'address': {'read_only': True},
        }
        fields = ('address', 'tx_hash', 'name', 'mails', 'test_node')

    def create(self, validated_data):
        return WeddingContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = TokenContract
        extra_kwargs = {
            'contract_type': {'read_only': True},
            'test_node': {'read_only': True},
            'address': {'read_only': True},
        }
        fields = ('address', 'tx_hash', 'name', 'addresses', 'contract_type', 'test_node')

    def create(self, validated_data):
        return TokenContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class HistoryResponseSerializer(serializers.Serializer):
    tokens = TokenSerializer()
    probates = ProbateSerializer()
    crowdsales = CrowdsaleSerializer()
    weddings = WeddingSerializer()
