from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from cblock.accounts.models import Profile
from cblock.accounts.permissions import IsAuthenticatedAndContractAdmin
from cblock.contracts.models import (
    TokenContract,
    TokenHolder,
    LastWillContract,
    LostKeyContract,
    CrowdsaleContract,
    WeddingContract,
    WeddingEmail,
    LastWillEmail,
    LostKeyEmail,
    CONTRACT_MODELS,
    NetworkMode
)
from cblock.contracts.serializers import (
    TokenSerializer,
    CrowdsaleSerializer,
    LastWillSerializer,
    LostKeySerializer,
    WeddingSerializer,
    HistoryResponseSerializer,
    LastWillListSerializer,
    LostKeyListSerializer,
    NetworkModeSerializer
)

from cblock.contracts.utils import check_terminated_contract
from cblock.settings import config

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
        profile = Profile.objects.get(owner_address__iexact=address.lower())
    except Profile.DoesNotExist:
        return Response(data={'Error': 'No such user address in the DB'}, status=HTTP_404_NOT_FOUND)

    profile_history = dict()
    for network in config.networks:
        token_contracts = TokenContract.objects.filter(owner=profile, is_testnet=network.is_testnet)
        crowdsale_contracts = CrowdsaleContract.objects.filter(owner=profile, is_testnet=network.is_testnet)
        lastwill_contracts = LastWillContract.objects.filter(owner=profile, is_testnet=network.is_testnet)
        lostkey_contracts = LostKeyContract.objects.filter(owner=profile, is_testnet=network.is_testnet)
        wedding_contracts = WeddingContract.objects.filter(owner=profile, is_testnet=network.is_testnet)

        network_history = {
            "tokens": TokenSerializer(token_contracts, many=True).data,
            "crowdsales": CrowdsaleSerializer(crowdsale_contracts, many=True).data,
            "lastwills": LastWillSerializer(lastwill_contracts, many=True).data,
            "lostkeys": LostKeySerializer(lostkey_contracts, many=True).data,
            "weddings": WeddingSerializer(wedding_contracts, many=True).data
        }
        profile_history[network.name] = network_history
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
    lastwills = LastWillContract.objects.filter(dead=True, terminated=False)
    lastwills = check_terminated_contract(lastwills)
    if not lastwills:
        return Response(status=HTTP_404_NOT_FOUND)

    contracts = dict()
    for network in config.networks:
        network_contracts = lastwills.filter(is_testnet=network.is_testnet)
        contracts[network.name] = LastWillListSerializer(network_contracts, many=True).data

    res = {
        'lastwills': contracts
    }
    return Response(data=res, status=HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="List dead user wallets (lostkey)",
    responses={'200': LostKeyListSerializer()}
)
@api_view(http_method_names=['GET'])
# @permission_classes([IsAuthenticated])
def lostkey_dead_list(request):
    """
    List 'dead' wallets with heirs
    :return: owner wallet address and list heirs mails
    """
    lostkeys = LostKeyContract.objects.filter(dead=True, terminated=False)
    lostkeys = check_terminated_contract(lostkeys)

    contracts = dict()
    for network in config.networks:
        network_contracts = lostkeys.filter(is_testnet=network.is_testnet)
        contracts[network.name] = LastWillListSerializer(network_contracts, many=True).data

    if not lostkeys:
        return Response(status=HTTP_404_NOT_FOUND)

    res = {
        'lostkeys': contracts
    }
    return Response(data=res, status=HTTP_200_OK)



"""
Views for create new user contract_abi
"""


@swagger_auto_schema(
    method='post',
    operation_description="Create new user lastwill contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'mails': openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                            'email': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='User address'),
                                            }
                                    ),
            'owner_mail': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the contract creator'),
            'is_testnet': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Testnet or mainnet contract')
        },
        required=['tx_hash', 'name', 'mails', 'owner_mail', 'is_testnet']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_lastwill(request):
    """
    Create new probate contract
    """
    heirs_emails = request.data.pop('mails')

    if len(heirs_emails) == 0:
        return Response(data={'Error': 'Requwst does not contain "mails" field'}, status=HTTP_400_BAD_REQUEST)

    probate = LastWillContract.objects.filter(tx_hash=request.data['tx_hash'])
    if probate.exists():
        serializer = LastWillSerializer(probate[0], data=request.data)
    else:
        serializer = LastWillSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    probate = serializer.save()

    existing_emails = LastWillEmail.objects.filter(probate_contract=probate)
    if existing_emails:
        existing_emails.delete()

    emails_objects_list = []
    for email, address in heirs_emails.items():
        logging.info(f'{email} - {address}')
        emails_objects_list.append(
            LastWillEmail(probate_contract=probate, email=email, address=address.lower())
        )

    LastWillEmail.objects.bulk_create(emails_objects_list)

    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user probate contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'mails': openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                            'email': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='User address'),
                                            }
                                    ),
            'owner_mail': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the contract creator'),
            'is_testnet': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Testnet or mainnet contract')
        },
        required=['tx_hash', 'name', 'mails', 'owner_mail', 'is_testnet']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_lostkey(request):
    """
    Create new probate contract
    """
    heirs_emails = request.data.pop('mails')

    if len(heirs_emails) == 0:
        return Response(data={'Error': 'Requwst does not contain "mails" field'}, status=HTTP_400_BAD_REQUEST)

    probate = LostKeyContract.objects.filter(tx_hash=request.data['tx_hash'])
    if probate.exists():
        serializer = LostKeySerializer(probate[0], data=request.data)
    else:
        serializer = LostKeySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    probate = serializer.save()

    existing_emails = LostKeyEmail.objects.filter(probate_contract=probate)
    if existing_emails:
        existing_emails.delete()

    emails_objects_list = []
    for email, address in heirs_emails.items():
        logging.info(f'{email} - {address}')
        emails_objects_list.append(
            LostKeyEmail(probate_contract=probate, email=email, address=address.lower())
        )

    LostKeyEmail.objects.bulk_create(emails_objects_list)

    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user crowdsale contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'is_testnet': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Testnet or mainnet contract')
        },
        required=['name', 'tx_hash', 'is_testnet']
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
            'mails': openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                        'email': openapi.Schema(type=openapi.TYPE_STRING,
                                                                description='Holder address'),
                                        }
                                    ),
            'is_testnet': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Testnet or mainnet contract')
        },
        required=['tx_hash', 'name', 'mails', 'is_testnet']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
# @permission_classes([IsAuthenticated])
def new_wedding(request):
    """
    Create new wedding contract
    """
    partners_emails = request.data.pop('mails')

    if len(partners_emails) != 2:
        return Response(data={'Error': 'There must be exactly 2 partner emails'}, status=HTTP_400_BAD_REQUEST)

    wedding = WeddingContract.objects.filter(tx_hash=request.data['tx_hash'])
    if wedding.exists():
        serializer = WeddingSerializer(wedding[0], data=request.data)
    else:
        serializer = WeddingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    wedding = serializer.save()

    existing_emails = WeddingEmail.objects.filter(wedding_contract=wedding)
    if existing_emails:
        existing_emails.delete()

    emails_objects_list = []
    for email, address in partners_emails.items():
        logging.info(f'{email} - {address}')
        emails_objects_list.append(
            WeddingEmail(wedding_contract=wedding, email=email, address=address.lower())
        )

    WeddingEmail.objects.bulk_create(emails_objects_list)

    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user token contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tx_hash': openapi.Schema(type=openapi.TYPE_STRING, description='Contract deploy hash'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='User contract name'),
            'addresses': openapi.Schema(type=openapi.TYPE_OBJECT,
                                        properties={
                                            'owner_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                         description='Holder address'),
                                            }
                                        ),
            'is_testnet': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Testnet or mainnet contract')
        },
        required=['tx_hash', 'name', 'addresses', 'is_testnet']
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
    token = serializer.save()

    existing_holders = TokenHolder.objects.filter(token_contract=token)
    if existing_holders:
        existing_holders.delete()

    holders_object_list = []
    for name, address in token_holders.items():
        logging.info(f'{name} - {address}')
        holders_object_list.append(
            TokenHolder(token_contract=token, name=name, address=address.lower())
        )

    TokenHolder.objects.bulk_create(holders_object_list)

    return Response(data={'Success': 'True'}, status=HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve platform statistics",
    responses={'200': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'users': openapi.Schema(type=openapi.TYPE_INTEGER, description='Active users'),
            'contracts': openapi.Schema(type=openapi.TYPE_INTEGER, description='Created contracts'),
        }
    )}
)
@api_view(http_method_names=['GET'])
def platform_statistics(request):
    """
    Returns platform statistics (users with deployed contracts and number of deployed contacts)
    """
    contracts_count = 0
    for key, model in CONTRACT_MODELS.items():
        contract_type_count = model.objects.count()
        contracts_count += contract_type_count

    profiles_count = Profile.objects.count()

    return Response(
        data={'users': profiles_count, 'contracts': contracts_count},
        status=HTTP_200_OK
    )

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve current network mode",
    responses={'200':NetworkModeSerializer()}
)
@api_view(http_method_names=['GET'])
def show_current_network_mode(request):
    """
    Returns current permission for deployments
    """
    network_mode, _ = NetworkMode.objects.get_or_create(name='celo')
    serialized_data = NetworkModeSerializer(instance=network_mode).data

    return Response(serialized_data)


@swagger_auto_schema(
    method='post',
    operation_description="Retrieve current network mode",
    request_body=NetworkModeSerializer,
    responses={'200':NetworkModeSerializer()}
)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticatedAndContractAdmin])
def update_network_mode(request):
    """
    Returns current permission for deployments
    """
    if 'mainnet_enabled' not in request.data:
        return Response(data={'Error': 'Requwst does not contain "mainnet_enabled" field'}, status=HTTP_400_BAD_REQUEST)

    new_status = request.data.get('mainnet_enabled')

    if not isinstance(new_status, bool):
        return Response(data={'Error': 'Only boolean values are acceptes'}, status=HTTP_400_BAD_REQUEST)

    network_mode, _ = NetworkMode.objects.get_or_create(name='celo')
    network_mode.mainnet_enabled = new_status
    network_mode.save()

    serialized_data = NetworkModeSerializer(instance=network_mode).data

    return Response(serialized_data)