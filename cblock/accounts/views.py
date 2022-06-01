from random import choice
from string import ascii_letters

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_auth.registration.views import SocialLoginView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cblock.accounts.models import Profile
from cblock.accounts.serializers import MetamaskLoginSerializer
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


@api_view(http_method_names=["GET"])
def generate_metamask_message(request):

    generated_message = "".join(choice(ascii_letters) for ch in range(30))
    request.session["metamask_message"] = generated_message

    return Response(generated_message)
