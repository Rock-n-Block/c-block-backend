from rest_framework import serializers

from cblock.rates.models import UsdRate


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsdRate
        fields = (
            "rate",
            "symbol",
            "name",
        )
