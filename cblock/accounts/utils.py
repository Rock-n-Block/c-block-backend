from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils.hexadecimal import add_0x_prefix

from rest_framework.exceptions import ValidationError

from cblock.config import config

def valid_metamask_message(address, message, signature) -> bool:
    r = int(signature[0:66], 16)
    s = int(add_0x_prefix(signature[66:130]), 16)
    v = int(add_0x_prefix(signature[130:132]), 16)
    if v not in (27, 28):
        v += 27

    message_hash = encode_defunct(text=message)
    signer_address = Account.recover_message(message_hash, vrs=(v, r, s))
    print(signer_address)
    print(address)

    if signer_address.lower() != address.lower():
        raise ValidationError({'result': 'Incorrect signature'}, code=400)

    return True

def get_domain_for_emails(request) -> str:
    return config.frontend_host_domain if config.frontend_host_domain else request.META.get('HTTP_HOST')
