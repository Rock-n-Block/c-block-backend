from dataclasses import dataclass
from scanner.components.base import (
    EventBase,
    NewContractBase,
    NewContractWithType,
    WeddingProposalBase,
    WeddingStatusBase
)


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
    decision_time_withdrawal: int
    decision_time_divorce: int


@dataclass
class NewContractLastWill(NewContractBase):
    confirmation_period: int
    last_recorded_time: int


@dataclass
class NewContractLostKey(NewContractBase):
    confirmation_period: int
    last_recorded_time: int


@dataclass
class TransferOwnership(EventBase):
    contract_address: str
    previous_owner: str
    new_owner: str


@dataclass
class WeddingWithdrawalProposed(WeddingProposalBase):
    receiver: str
    token_amount: int
    token: str


@dataclass
class WeddingWithdrawalStatusChanged(WeddingStatusBase):
    executed_by: str


@dataclass
class WeddingDivorceProposed(WeddingProposalBase):
    pass


@dataclass
class WeddingDivorceStatusChanged(WeddingStatusBase):
    pass

@dataclass
class ProbateFundsDistributed(EventBase):
    contract_address: str
    backup_addresses: list
