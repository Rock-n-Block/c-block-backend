from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Profile, TokenContract, ProbateContract, CrowdsaleContract, WeddingContract
from .serializers import (TokenSerializer, CrowdsaleSerializer, ProbateSerializer, WeddingSerializer,
                          HistoryResponseSerializer, ProbateListSerializer)

import logging

logger = logging.getLogger('__name__')
@swagger_auto_schema(
    method='get',
    operation_description="User contract history",
    responses={'200': HistoryResponseSerializer(),
               '404': 'No such user address in the DB'}
)
@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated])
def history(request, address: str):
    """
    Account(address) history.
    :return: contract list with information which created this owner
    """
    profile = Profile.objects.filter(owner_address__iexact=address).first()
    if not profile:
        return Response(data={'Error': 'No such user address in the DB'}, status=HTTP_404_NOT_FOUND)
    token_contracts = TokenContract.objects.filter(owner=profile)
    crowdsale_contracts = CrowdsaleContract.objects.filter(owner=profile)
    probate_contracts = ProbateContract.objects.filter(owner=profile)
    wedding_contracts = WeddingContract.objects.filter(owner=profile)
    history = dict()
    history['tokens'] = TokenSerializer(token_contracts, many=True).data
    history['crowdsales'] = CrowdsaleSerializer(crowdsale_contracts, many=True).data
    history['probates'] = ProbateSerializer(probate_contracts, many=True).data
    history['weddings'] = WeddingSerializer(wedding_contracts, many=True).data
    return Response(data=history, status=HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="List dead user wallets",
    responses={'200': ProbateListSerializer()}
)
@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticated])
def probates(request):
    """
    List 'dead' wallets with heirs
    :return: owner wallet address and list heirs mails
    """
    probate_list = ProbateContract.objects.filter(dead=True, terminated=False)

    [ProbateListSerializer(probate) for probate in probate_list]
    return Response(data=ProbateListSerializer, status=HTTP_200_OK)


"""
Views for create new user contracts
"""
@swagger_auto_schema(
    method='post',
    operation_description="Create new user probate contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'owner_address': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'contract_address': openapi.Schema(type=openapi.TYPE_STRING, description='Contract address'),
            'contract_name': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'mail_list': openapi.Schema(type=openapi.TYPE_ARRAY, description='Heirs mail list(max 4)',
                                        items=openapi.TYPE_STRING),
            'owner_mail': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the contract creator'),
        },
        required=['owner_address', 'contract_address', 'contract_name', 'mail_list', 'owner_mail']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def new_probate(request):
    """
    Create new probate contract
    """
    owner, created = Profile.objects.get_or_create(owner_address=request.data['owner_address'])
    serializer = ProbateSerializer(data={
        'address': request.data['contract_address'],
        'name': request.data['contract_name'],
        'mails_array': request.data['mail_list'],
        'owner': owner.pk,
        'owner_mail': request.data['owner_mail'],
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user crowdsale contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'owner_address': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'contract_name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'contract_address': openapi.Schema(type=openapi.TYPE_STRING, description='Contract address'),
        },
        required=['owner_address', 'contract_name', 'contract_address']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def new_crowdsale(request):
    """
    Create new crowdsale contract
    """
    owner, created = Profile.objects.get_or_create(owner_address=request.data['owner_address'])

    serializer = CrowdsaleSerializer(data={
        'address': request.data['contract_address'],
        'name': request.data['contract_name'],
        'owner': owner.pk
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user wedding contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'owner_address': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'contract_address': openapi.Schema(type=openapi.TYPE_STRING, description='Contract address'),
            'contract_name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'mail_list': openapi.Schema(type=openapi.TYPE_ARRAY, description='User wallet list(max 2)',
                                        items=openapi.TYPE_STRING),
        },
        required=['owner_address', 'contract_address', 'contract_name', 'mail_list']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def new_wedding(request):
    """
    Create new wedding contract
    """
    owner, created = Profile.objects.get_or_create(owner_address=request.data['owner_address'])
    serializer = WeddingSerializer(data={
        'address': request.data['contract_address'],
        'name': request.data['contract_name'],
        'mail_list': request.data['mail_list'],
        'owner': owner.pk
    })
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user token contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'owner_address': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'contract_address': openapi.Schema(type=openapi.TYPE_STRING, description='Contract address'),
            'contract_name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'address_list': openapi.Schema(type=openapi.TYPE_ARRAY, description='User wallet list(max 5)',
                                        items=openapi.TYPE_ARRAY),
        },
        required=['owner_address', 'contract_address', 'contract_name', 'address_list']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def new_token(request):
    """
    Create new token contract
    """
    owner, created = Profile.objects.get_or_create(owner_address=request.data['owner_address'])

    serializer = TokenSerializer(data={
        'address': request.data['contract_address'],
        'address_list': request.data['address_list'],
        'name': request.data['contract_name'],
        'owner': owner.pk}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={'Success': 'True'}, status=HTTP_200_OK)
