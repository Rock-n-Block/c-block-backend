import json
from pathlib import Path


with Path("scanner", "contracts", "erc20nmnf_fabric.json").open() as f:
    ERC20NMNF_FABRIC = json.load(f)

with Path("scanner", "contracts", "erc20nmf_fabric.json").open() as f:
    ERC20NMF_FABRIC = json.load(f)

with Path("scanner", "contracts", "erc20mnf_fabric.json").open() as f:
    ERC20MNF_FABRIC = json.load(f)

with Path("scanner", "contracts", "erc20mf_fabric.json").open() as f:
    ERC20MF_FABRIC = json.load(f)
