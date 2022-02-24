from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

<<<<<<< HEAD
from scanner.models import Profile, TokenContract, TokenHolder, ProbateContract, CrowdsaleContract, WeddingContract
from scanner.serializers import (TokenSerializer, CrowdsaleSerializer, ProbateSerializer, WeddingSerializer,
                          HistoryResponseSerializer, ProbateListSerializer)
=======
>>>>>>> add token holder names
from scanner.models import Profile, TokenContract, TokenHolder, LastWillContract, LostKeyContract, CrowdsaleContract,\
    WeddingContract
from scanner.serializers import (TokenSerializer, CrowdsaleSerializer, LastWillSerializer, LostKeySerializer,
                                 WeddingSerializer, HistoryResponseSerializer, LastWillListSerializer,
                                 LostKeyListSerializer)
from scanner.utils import check_terminated_contract

import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='get',
    operation_description="User contract history",
    responses={'200': HistoryResponseSerializer(),
               '404': 'No such user address in the DB'}
)
@api_view(http_method_names=['GET'])
#@permission_classes([IsAuthenticated])
def history(request, address: str):
    """
    Account(address) history.
    :return: contract list with information which created this owner
    """
    try:
        profile = Profile.objects.get(owner_address__iexact=address)
    except Profile.DoesNotExist:
        return Response(data={'Error': 'No such user address in the DB'}, status=HTTP_404_NOT_FOUND)
    token_contracts = TokenContract.objects.filter(owner=profile)
    crowdsale_contracts = CrowdsaleContract.objects.filter(owner=profile)
    lastwill_contracts = LastWillContract.objects.filter(owner=profile)
    lostkey_contracts = LostKeyContract.objects.filter(owner=profile)
    wedding_contracts = WeddingContract.objects.filter(owner=profile)
    profile_history = dict()
    profile_history['tokens'] = TokenSerializer(token_contracts, many=True).data
    profile_history['crowdsales'] = CrowdsaleSerializer(crowdsale_contracts, many=True).data
    profile_history['lastwills'] = LastWillSerializer(lastwill_contracts, many=True).data
    profile_history['lostkeys'] = LostKeySerializer(lostkey_contracts, many=True).data
    profile_history['weddings'] = WeddingSerializer(wedding_contracts, many=True).data
    return Response(data=profile_history, status=HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="List dead user wallets (lastwill)",
    responses={'200': LastWillListSerializer()}
)
@api_view(http_method_names=['GET'])
# @permission_classes([IsAuthenticated])
def lastwill_dead_list(request):
    """
    List 'dead' wallets with heirs
    :return: owner wallet address and list heirs mails
    """
    lastwills = LastWillContract.objects.filter(dead=True, terminated=False, test_node=False)
    lastwills = check_terminated_contract(lastwills)
    if not lastwills.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    lastwills['lastwills'] = LastWillListSerializer(lastwills, many=True).data
    return Response(data=lastwills, status=HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="List dead user wallets (lastwill)",
    responses={'200': LastWillListSerializer()}
)
@api_view(http_method_names=['GET'])
# @permission_classes([IsAuthenticated])
def lostkey_dead_list(request):
    """
    List 'dead' wallets with heirs
    :return: owner wallet address and list heirs mails
    """
    lostkeys = LostKeyContract.objects.filter(dead=True, terminated=False, test_node=False)
    lostkeys = check_terminated_contract(lostkeys)
    if not lostkeys.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    lostkeys['lostkeys'] = LostKeyListSerializer(lostkeys, many=True).data
    return Response(data=lostkeys, status=HTTP_200_OK)



"""
Views for create new user contracts
"""


@swagger_auto_schema(
    method='post',
    operation_description="Create new user lastwill contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'mails': openapi.Schema(type=openapi.TYPE_ARRAY, description='Heirs mail list(max 4)',
                                        items=openapi.TYPE_STRING),
            'owner_mail': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the contract creator'),
        },
        required=['tx_hash', 'name', 'mails', 'owner_mail']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_lastwill(request):
    """
    Create new probate contract
    """
    probate = LastWillContract.objects.filter(tx_hash=request.data['tx_hash'])
    if probate.exists():
        serializer = LastWillSerializer(probate[0], data=request.data)
    else:
        serializer = LastWillSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user probate contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'mails': openapi.Schema(type=openapi.TYPE_ARRAY, description='Heirs mail list(max 4)',
                                        items=openapi.TYPE_STRING),
            'owner_mail': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the contract creator'),
        },
        required=['tx_hash', 'name', 'mails', 'owner_mail']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_lostkey(request):
    """
    Create new probate contract
    """
    probate = LostKeyContract.objects.filter(tx_hash=request.data['tx_hash'])
    if probate.exists():
        serializer = LostKeySerializer(probate[0], data=request.data)
    else:
        serializer = LostKeySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user crowdsale contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
        },
        required=['name', 'tx_hash']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_crowdsale(request):
    """
    Create new crowdsale contract
    """
    crowdsale = CrowdsaleContract.objects.filter(tx_hash=request.data['tx_hash'])
    if crowdsale.exists():
        serializer = CrowdsaleSerializer(crowdsale[0], data=request.data)
    else:
        serializer = CrowdsaleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user wedding contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'mails': openapi.Schema(type=openapi.TYPE_ARRAY, description='User wallet list(max 2)',
                                        items=openapi.TYPE_STRING),
        },
        required=['tx_hash', 'name', 'mails']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_wedding(request):
    """
    Create new wedding contract
    """
    wedding = WeddingContract.objects.filter(tx_hash=request.data['tx_hash'])
    if wedding.exists():
        serializer = WeddingSerializer(wedding[0], data=request.data)
    else:
        serializer = WeddingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user token contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'addresses': openapi.Schema(type=openapi.TYPE_ARRAY,
                                        description='User wallet list(max 5)',
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Holder name'),
                                                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Holder address'),
                                            }
                                        )),
        },
        required=['tx_hash', 'name', 'addresses']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_token(request):
    """
    Create new token contract
    """
    token = TokenContract.objects.filter(tx_hash=request.data['tx_hash'])
    token_holders = request.data.pop('addresses')

    if token.exists():
        serializer = TokenSerializer(token[0], data=request.data)
    else:
        serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    existing_holders = TokenHolder.objects.filter(token_contract=token)
    if existing_holders:
        existing_holders.delete()

    holders_object_list = []
    for name, address in token_holders.items():
        holders_object_list.append(
            TokenHolder(token_contract=token, name=name, address=address)
        )

    TokenHolder.objects.bulk_create(holders_object_list)

    return Response(data={'Success': 'True'}, status=HTTP_200_OK)
