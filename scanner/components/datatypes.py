from dataclasses import dataclass
from scanner.components.base import EventBase, NewContractBase, NewContractWithType, WeddingBase


@dataclass
class NewContractToken(NewContractWithType):
    pass


@dataclass
class NewContractCrowdsale(NewContractWithType):
    pass


@dataclass
class NewContractWedding(NewContractBase):
    owner_first: str
    owner_second: str


@dataclass
class NewContractLastWill(NewContractBase):
    pass


@dataclass
class NewContractLostKey(NewContractBase):
    pass


@dataclass
class WeddingWithdrawalProposed(WeddingBase):
    receiver: str
    token_amount: int
    token: str


@dataclass
class WeddingDivorceProposed(WeddingBase):
    pass


@dataclass
class TransferOwnership(EventBase):
    contract_address: str
    previous_owner: str
    new_owner: str

