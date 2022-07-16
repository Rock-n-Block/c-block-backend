import logging
import json

from random import choice
from string import ascii_letters

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail

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

from cblock.accounts.models import Profile, ControllerSuperAdmin, ControllerPriceAdmin, ControllerPaymentAddressesAdmin
from cblock.accounts.serializers import MetamaskLoginSerializer, MetamaskUserSerializer
from cblock.accounts.permissions import (
    PERMISSION_LIST_USERS,
    PERMISSION_LIST_CONTRACTS,
    update_permission_value,
    check_admin_rights
)

from cblock.mails.mail_messages import EMAIL_TEXTS
from cblock.settings import config

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

    @swagger_auto_schema(
        operation_description="get info of country codes",
        responses={200: openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'country_code': openapi.Schema(type=openapi.TYPE_STRING),
                    'country_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'phone_code': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        )}
    )
    def get(self, request):
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



class UserListView(ListAPIView):
    queryset =  Profile.objects.exclude(
        owner_address__in=["", "0x0000000000000000000000000000000000000000000000000000000000000000"]
    )
    serializer_class = MetamaskUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        user_data = super().get_object()

    def get(self, request, *args, **kwargs):
        user: Profile = request.user

        perms = check_admin_rights(user, ControllerSuperAdmin, PERMISSION_LIST_USERS.get('can_view_users'))
        if not perms:
            raise PermissionDenied()

        return super().get(request, *args, **kwargs)

class AdminPermissionUpdateView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_description="update permissions for user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                "can_view_users": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "can_freeze_users": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "can_contact_users": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "can_change_network_mode": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
            required=["id"]
        ),
        responses={200: "OK", 400: "Bad request", 404: "User not found"}
    )
    def post(self, request):
        user = request.user
        perms = check_admin_rights(user, ControllerSuperAdmin)
        if not perms:
            raise PermissionDenied()

        try:
            user = Profile.objects.get(id=request.data.get('id'))
        except ObjectDoesNotExist:
            return Response(
                {"error": USER_NOT_FOUND_RESPONSE}, status=status.HTTP_404_NOT_FOUND
            )

        if len(request.data.keys()) < 2:
            return Response(
                {"error": "at least 1 permission must be passed"}, status=status.HTTP_400_BAD_REQUEST
            )

        can_view_users = request.data.get('can_view_users')
        if can_view_users is not None:
            update_permission_value(can_view_users, PERMISSION_LIST_USERS.get('can_view_users'), user)

        can_freeze_users = request.data.get('can_freeze_users')
        if can_freeze_users is not None:
            update_permission_value(can_freeze_users,PERMISSION_LIST_USERS.get('can_freeze_users'), user)

        can_contact_users = request.data.get('can_contact_users')
        if can_contact_users is not None:
            update_permission_value(can_contact_users, PERMISSION_LIST_USERS.get('can_contact_users'), user)

        # Setting `view` permission if it was not passed
        if (can_freeze_users or can_contact_users) and not can_view_users:
            update_permission_value(True, PERMISSION_LIST_USERS.get('can_view_users'), user)

        can_change_network_mode = request.data.get('can_change_network_mode')
        if can_change_network_mode is not None:
            from cblock.contracts.models import NetworkMode
            network_mode_obj, _ = NetworkMode.objects.get_or_create(name='celo')
            update_permission_value(
                can_change_network_mode,
                PERMISSION_LIST_CONTRACTS.get('can_change_network_mode'),
                user,
                network_mode_obj
            )

        response_data = MetamaskUserSerializer(user).data
        return Response(response_data)


class UserFreezeView(APIView):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_description="freeze user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                "freezed": openapi.Schema(type=openapi.TYPE_BOOLEAN)
            },
            required=["id", "freezed"]
        ),
        responses={200: "OK", 400: "Bad request", 404: "User not found"}
    )
    def post(self, request):
        user = request.user
        perms = check_admin_rights(user, ControllerSuperAdmin, PERMISSION_LIST_USERS.get('can_freeze_users'))
        if not perms:
            raise PermissionDenied()

        freezed = request.data.get('freezed')

        try:
            user = Profile.objects.get(id=request.data.get('id'))
        except ObjectDoesNotExist:
            return Response(
                {"error": USER_NOT_FOUND_RESPONSE}, status=status.HTTP_404_NOT_FOUND
            )

        user.freezed = freezed
        user.save()

        response_data = MetamaskUserSerializer(user).data
        return Response(response_data)

class UserContactView(APIView):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_description="contact user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                "message": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=["id", "freezed"]
        ),
        responses={200: "OK", 400: "Bad request", 404: "User not found"}
    )
    def post(self, request):
        user = request.user
        perms = check_admin_rights(user, ControllerSuperAdmin, PERMISSION_LIST_USERS.get('can_contact_users'))
        if not perms:
            raise PermissionDenied()

        message = request.data.get('message')

        try:
            user = Profile.objects.get(id=request.data.get('id'))
        except ObjectDoesNotExist:
            return Response(
                {"error": USER_NOT_FOUND_RESPONSE}, status=status.HTTP_404_NOT_FOUND
            )

        message_text_title = EMAIL_TEXTS.get('admin').get('contact').get('title')
        send_mail(
            message_text_title,
            message,
            from_email=config.email_host_user,
            recipient_list=[user.email],
            fail_silently=True
        )

        return Response({"result": "ok"})