import json
from pathlib import Path

with Path("contract_abi", "token_factory.json").open() as f:
    TOKEN_FACTORY_ABI = json.load(f)

with Path("contract_abi", "crowdsale_factory.json").open() as f:
    CROWDSALE_FACTORY_ABI = json.load(f)

with Path("contract_abi", "wedding_factory.json").open() as f:
    WEDDING_FACTORY_ABI = json.load(f)

with Path("contract_abi", "probate_factory.json").open() as f:
    PROBATE_FACTORY_ABI = json.load(f)

with Path("contract_abi", "probate.json").open() as f:
    PROBATE_ABI = json.load(f)

with Path("contract_abi", "wedding.json").open() as f:
    WEDDING_ABI = json.load(f)

with Path("contract_abi", "ownable.json").open() as f:
    OWNABLE_ABI = json.load(f)
