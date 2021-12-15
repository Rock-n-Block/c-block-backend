import json
from pathlib import Path


with Path("scanner", "contracts", "probate.json").open() as f:
    PROBATE_FABRIC_ABI = json.load(f)
