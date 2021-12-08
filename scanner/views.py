from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Profile, TokenContract, ProbateContract, CrowdsaleContract, WeddingContract

import logging

logger = logging.getLogger('__name__')
@swagger_auto_schema(
    method='get',
    operation_description="User contract history",
    responses={'200': 'Success',
               '404': 'No such user address in the DB'}
)
@api_view(http_method_names=['GET'])
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
    history['token'] = [{
        'address': contract.address,
        'address_list': contract.address_list,
        'contract_type': contract.contract_type,
        'test_noda': contract.test_noda
    } for contract in token_contracts]
    history['crowdsale'] = [{
        'address': contract.address,
        'contract_name': contract.name,
        'test_noda': contract.test_noda
    } for contract in crowdsale_contracts]
    history['probate'] = [{
        'address': contract.address,
        'contract_name': contract.name,
        'mails_list': contract.mails_array,
        'owner_mail': contract.owner_mail,
        'test_noda': contract.test_noda
    } for contract in probate_contracts]
    history['wedding'] = [{
        'address': contract.address,
        'contract_name': contract.name,
        'mail_list': contract.mail_list,
        'test_noda': contract.test_noda
    } for contract in wedding_contracts]
    return Response(data=history, status=HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="List dead user wallets",
    responses={'200': 'Success'}
)
@api_view(http_method_names=['GET'])
def probates(request):
    """
    List 'dead' wallets with heirs
    :return: owner wallet address and list heirs mails
    """
    probate_list = ProbateContract.objects.filter(dead=True)

    data = list()
    [data.append({
        'owner_address': probate.owner.owner_address,
        'mails': probate.mails_array
    }) for probate in probate_list]
    return Response(data=data, status=HTTP_200_OK)


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
            'identifier': openapi.Schema(type=openapi.TYPE_STRING, description='ID for check contract'),
            'owner_mail': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the contract creator'),
            # 'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type lost_key or dead'),
        },
        required=['owner_address', 'contract_address', 'contract_name', 'mail_list', 'identifier', 'owner_mail']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
def new_probate(request):
    """
    Create new probate contract
    """
    owner = Profile.objects.get_or_create(owner_address=request.data['owner_address'])
    ProbateContract.objects.update_or_create(
        address=request.data['contract_address'],
        name=request.data['contract_name'],
        mails_array=request.data['mail_list'],
        identifier=request.data['identifier'],
        owner=owner[0],
        owner_mail=request.data['owner_mail'],
    )
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
def new_crowdsale(request):
    """
    Create new crowdsale contract
    """
    owner = Profile.objects.get_or_create(owner_address=request.data['owner_address'])

    CrowdsaleContract.objects.update_or_create(
        address=request.data['contract_address'],
        name=request.data['contract_name'],
        owner=owner[0])
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
def new_wedding(request):
    """
    Create new wedding contract
    """
    owner = Profile.objects.get_or_create(owner_address=request.data['owner_address'])
    WeddingContract.objects.update_or_create(
        address=request.data['contract_address'],
        name=request.data['contract_name'],
        mail_list=request.data['mail_list'],
        owner=owner[0]
    )
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
def new_token(request):
    """
    Create new token contract
    """
    owner = Profile.objects.get_or_create(owner_address=request.data['owner_address'])

    TokenContract.objects.update_or_create(
        address=request.data['contract_address'],
        address_list=request.data['address_list'],
        name=request.data['contract_name'],
        owner=owner[0]
    )
    return Response(data={'Success': 'True'}, status=HTTP_200_OK)
