from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Profile, TokenContract, ProbateContract


@swagger_auto_schema(
    method='get',
    operation_description="User contract history",
    responses={'200': 'Success',
               '404': 'No such user address in the DB'}
)
@api_view(http_method_names=['GET'])
def history(request, address):
    """
    Account(address) history.
    :return: contract list with information which created this owner
    """
    profile = Profile.objects.filter(owner_address__iexact=address).first()
    if not profile:
        return Response(status=HTTP_404_NOT_FOUND)
    contracts = TokenContract.objects.filter(contracts=profile)
    history = list()
    for contract in contracts:
        history.append({
            'address': contract.address,
            'deploy_block': contract.deploy_block,
            'contract_type': contract.contract_type,
            'test_noda': contract.test_noda
        })
    return Response(data=history, status=HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="List dead user wallets",
    responses={'200': 'Success',
               '404': 'No such user address in the DB'}
)
@api_view(http_method_names=['GET'])
def probate(request):
    """
    List 'dead' wallets with heirs
    :return: owner wallet address and list heirs mails
    """
    probate_list = ProbateContract.objects.filter(dead=True)

    if not probate_list:
        return Response(status=HTTP_200_OK)
    data = list()
    for probate in probate_list:
        data.append({
            'owner_address': probate.owner.owner_address,
            'mails': probate.mails_array
        })
    return Response(data=data, status=HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Create new user probate contract",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'address': openapi.Schema(type=openapi.TYPE_STRING, description='Owner wallet address'),
            'mail_list': openapi.Schema(type=openapi.TYPE_ARRAY, description='Heirs mail list(max 4)',
                                        items=openapi.TYPE_STRING),
            'identifier': openapi.Schema(type=openapi.TYPE_STRING, description='ID for check contract'),
            'owner_mail': openapi.Schema(type=openapi.TYPE_STRING),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description='Type lost_key or dead'),
        },
        required=['address', 'mail_list', 'identifier', 'owner_mail', 'type']
    ),
    responses={'200': 'Success'}
)
@api_view(http_method_names=['POST'])
def mail_list(request):
    """
    Create to database new probate contract
    """
    owner = Profile.objects.get_or_create(owner_address=request.data['address'])[0]
    ProbateContract.objects.create(
        address=request.data['address'],
        mail_list=request.data['mail_list'],
        identifier=request.data['identifier'],
        owner=owner,
        owner_mail=request.data['owner_mail'],
        type=request.data['type'])

    return Response(status=HTTP_200_OK)
