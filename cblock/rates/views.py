from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cblock.rates.models import UsdRate
from cblock.rates.serializers import RateSerializer


class RateRequest(APIView):
    @swagger_auto_schema(
        operation_description="rate request",
        responses={200: RateSerializer()},
    )
    def get(self, request):
        rates = UsdRate.objects.all()
        response_data = RateSerializer(rates, many=True).data
        return Response(response_data, status=status.HTTP_200_OK)
