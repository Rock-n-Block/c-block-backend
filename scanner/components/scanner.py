from scanner.components.base import ScannerABC
from scanner.components.mixins import (
    NewContractTokenMixin,
    NewContractCrowdsaleMixin,
    NewContractWeddingMixin,
    NewContractLastwillMixin,
    NewContractLostkeyMixin,
    TransferOwnershipMixin,
    WeddingWithdrawalProposedMixin,
    WeddingWithdrawalStatusChangedMixin,
    WeddingDivorceProposedMixin,
    WeddingDivorceStatusChangeddMixin,
    ProbateFundsDistributedMixin
)


class Scanner(
    ScannerABC,
    NewContractTokenMixin,
    NewContractCrowdsaleMixin,
    NewContractWeddingMixin,
    NewContractLastwillMixin,
    NewContractLostkeyMixin,
    TransferOwnershipMixin,
    WeddingWithdrawalProposedMixin,
    WeddingWithdrawalStatusChangedMixin,
    WeddingDivorceProposedMixin,
    WeddingDivorceStatusChangeddMixin,
    ProbateFundsDistributedMixin
):
    def get_last_network_block(self) -> int:
        return self.network.w3.eth.blockNumber
