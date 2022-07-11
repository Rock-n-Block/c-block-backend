from random import choice
from string import ascii_letters

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_auth.registration.views import SocialLoginView
from rest_auth.registration.serializers import VerifyEmailSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from cblock.accounts.models import Profile
from cblock.accounts.serializers import MetamaskLoginSerializer, MetamaskUserSerializer
from web3 import Web3


class MetamaskUserDetailsView(RetrieveUpdateAPIView):
    serializer_class = MetamaskUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.none()

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        data = ret.data
        instance: Profile = self.get_object()
        extra_data = {'is_completed_profile': instance.is_completed_profile()}
        data.update(extra_data)
        return Response(data)

@api_view(http_method_names=["GET"])
def generate_metamask_message(request):

    generated_message = "".join(choice(ascii_letters) for ch in range(30))
    request.session["metamask_message"] = generated_message

    return Response(generated_message)

