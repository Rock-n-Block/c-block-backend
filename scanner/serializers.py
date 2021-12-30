from rest_framework import serializers

from .models import TokenContract, ProbateContract, WeddingContract, CrowdsaleContract


class ProbateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProbateContract
        fields = ('address', 'mail_list', 'owner_mail')


class ProbateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProbateContract
        extra_kwargs = {
            'test_node': {'read_only': True},
            'address': {'read_only': True}
        }
            
        fields = ('address', 'tx_hash', 'name', 'mail_list', 'owner_mail', 'test_node')

    def create(self, validated_data):
        return ProbateContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.tx_hash = validated_data.get('tx_hash', instance.tx_hash)
        instance.name = validated_data.get('name', instance.name)
        instance.mail_list = validated_data.get('mail_list', instance.mail_list)
        instance.owner_mail = validated_data.get('owner_mail', instance.owner_mail)
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
        instance.tx_hash = validated_data.get('tx_hash', instance.tx_hash)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance


class WeddingSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeddingContract
        extra_kwargs = {
            'test_node': {'read_only': True},
            'address': {'read_only': True},
        }
        fields = ('address', 'tx_hash', 'name', 'mail_list', 'test_node')

    def create(self, validated_data):
        return WeddingContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.tx_hash = validated_data.get('tx_hash', instance.tx_hash)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.mail_list = validated_data.get('mail_list', instance.mail_list)
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
        fields = ('address', 'tx_hash', 'name', 'address_list', 'contract_type', 'test_node')

    def create(self, validated_data):
        return TokenContract.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.tx_hash = validated_data.get('tx_hash', instance.tx_hash)
        instance.name = validated_data.get('name', instance.name)
        instance.address_list = validated_data.get('address_list', instance.address_list)
        instance.save()
        return instance


class HistoryResponseSerializer(serializers.Serializer):
    tokens = TokenSerializer()
    probates = ProbateSerializer()
    crowdsales = CrowdsaleSerializer()
    weddings = WeddingSerializer()
