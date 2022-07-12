from random import choice
from string import ascii_letters

from django.contrib.auth import get_user_model

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from django_countries import countries
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

from cblock.accounts.models import Profile
from cblock.accounts.serializers import MetamaskLoginSerializer, MetamaskUserSerializer


class MetamaskUserDetailsView(RetrieveUpdateAPIView):
    serializer_class = MetamaskUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.none()

    # @swagger_auto_schema(
    #     operation_description="Update current user info",
    #     # parser_classes=(MultiPartParser,),
    #     # request_body=MetamaskUserSerializer,
    #     manual_parameters=[openapi.Parameter('avatar', openapi.IN, type=openapi.TYPE_BOOLEAN)],
    #     responses={200: MetamaskUserSerializer, 400: "attr: this attr is occupied"},
    # )
    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        data = ret.data
        instance: Profile = self.get_object()
        extra_data = {'is_completed_profile': instance.is_completed_profile()}
        data.update(extra_data)
        return Response(data)

    @swagger_auto_schema(
        operation_description="Update current user info",
        parser_classes=(MultiPartParser,),
        request_body=MetamaskUserSerializer,
        manual_parameters=[openapi.Parameter('avatar', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN)],
        responses={200: MetamaskUserSerializer, 400: "attr: this attr is occupied"},
    )
    def put(self, request, *args, **kwargs):
        super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partial update current user info",
        parser_classes=(MultiPartParser,),
        request_body=MetamaskUserSerializer,
        manual_parameters=[openapi.Parameter('avatar', openapi.IN_FORM, type=openapi.TYPE_BOOLEAN)],
        responses={200: MetamaskUserSerializer, 400: "attr: this attr is occupied"},
    )
    def patch(self, request, *args, **kwargs):
        super().patch(request, *args, **kwargs)

class GenerateMetamaskMessageView(APIView):
    @staticmethod
    def get(request):
        generated_message = "".join(choice(ascii_letters) for ch in range(30))
        request.session["metamask_message"] = generated_message

        return Response(generated_message)


def get_phone_code(iso):
  for code, isos in COUNTRY_CODE_TO_REGION_CODE.items():
    if iso.upper() in isos:
        return code
  return None


class RetrieveCountryInfoView(APIView):

    @staticmethod
    def get(request):
        countries_list = list(countries)
        countries_with_phone_code = []
        for code, country_name in countries_list:
            country_info = {
                'country_code': code,
                'country_name': country_name,
                'phone_code': get_phone_code(code)
            }
            countries_with_phone_code.append(country_info)

        return Response(countries_with_phone_code)



