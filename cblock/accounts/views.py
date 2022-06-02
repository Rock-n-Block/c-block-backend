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
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from cblock.accounts.models import Profile
from cblock.accounts.serializers import MetamaskLoginSerializer, MetamaskUserSerializer
from web3 import Web3


class MetamaskLoginView(SocialLoginView):
    serializer_class = MetamaskLoginSerializer

    def login(self):

        self.user = self.serializer.validated_data["user"]
        metamask_address = Web3.toChecksumAddress(
                self.serializer.validated_data["address"]
            )

        try:
            user = Profile.objects.get(username__iexact=metamask_address)
        except ObjectDoesNotExist:
            print("try create user", flush=True)
            self.user = Profile(
                username=metamask_address, password=set_unusable_password()
            )
            self.user.save()
            print("user_created", flush=True)

        return super().login()

class MetamaskUserDetailsView(RetrieveAPIView):
    serializer_class = MetamaskUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.none()


@api_view(http_method_names=["GET"])
def generate_metamask_message(request):

    generated_message = "".join(choice(ascii_letters) for ch in range(30))
    request.session["metamask_message"] = generated_message

    return Response(generated_message)


# class VerifyEmailView(APIView, ConfirmEmailView):
#     permission_classes = (AllowAny,)
#     allowed_methods = ('POST', 'OPTIONS', 'HEAD')
#
#     def get_serializer(self, *args, **kwargs):
#         return VerifyEmailSerializer(*args, **kwargs)
#
#     def post(self, request, key):
#         data = key
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         self.kwargs['key'] = serializer.validated_data['key']
#         confirmation = self.get_object()
#         confirmation.confirm(self.request)
#         return Response({'detail': _('ok')}, status=status.HTTP_200_OK)