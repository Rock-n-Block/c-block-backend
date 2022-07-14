import logging
import json

from random import choice
from string import ascii_letters

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.serializers import ModelSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import status

from django_countries import countries
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

from cblock.accounts.models import Profile
from cblock.accounts.serializers import MetamaskLoginSerializer, MetamaskUserSerializer
from cblock.accounts.permissions import IsAuthenticatedAndContractSuperAdmin, update_permission_value

USER_NOT_FOUND_RESPONSE = "user not found"

class MetamaskUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user info",
        responses={200: MetamaskUserSerializer},
    )
    def get(self, request):
        response_data = MetamaskUserSerializer(request.user).data
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update user info",
        request_body=MetamaskUserSerializer,
        responses={200: MetamaskUserSerializer},
    )
    def patch(self, request):
        user = request.user
        request_data = request.data

        # handling multipart form data
        if list(request_data.keys()) == ['data', 'avatar']:
             multipart_data = request_data.get('data')
             request_data = json.loads(multipart_data)

        avatar = request.FILES.get('avatar')
        if avatar:
            request_data.pop('avatar', None)
            request_data['avatar'] = avatar

        serializer = MetamaskUserSerializer(user, data=request_data, partial=True)
        if serializer.is_valid():
            res = serializer.save()
        if serializer.errors:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_data = MetamaskUserSerializer(user).data
        return Response(response_data)

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



class UserListView(PermissionRequiredMixin, ListAPIView):
    queryset =  Profile.objects.exclude(owner_address="")
    serializer_class = MetamaskUserSerializer
    permission_classes = (IsAuthenticated,)
    permission_required = 'accounts.view_profile'

    def get_object(self):
        user_data = super().get_object()

class AdminPermissionUpdateView(APIView):
    permission_classes = [IsAuthenticatedAndContractSuperAdmin,]

    def post(self, request):
        user_id = request.data.get('id')

        try:
            user = Profile.objects.get(id=request.data.get('id'))
        except ObjectDoesNotExist:
            return Response(
                {"error": USER_NOT_FOUND_RESPONSE}, status=status.HTTP_404_NOT_FOUND
            )

        can_view_users = request.data.get('can_view_users')
        if can_view_users is not None:
            update_permission_value(
                can_view_users,
                'accounts.view_profile',
                user
            )

        can_change_network_mode = request.data.get('can_change_network_mode')
        if can_change_network_mode is not None:
            from cblock.contracts.models import NetworkMode
            network_mode_obj = NetworkMode.objects.get_or_create(name='celo')

            update_permission_value(
                can_change_network_mode,
                'contracts.edit_networkmode',
                user,
                network_mode_obj
            )

        response_data = MetamaskUserSerializer(user).data
        return Response(response_data)


