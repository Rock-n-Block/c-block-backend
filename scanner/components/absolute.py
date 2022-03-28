import threading

from scanner.components.scanner import Scanner
from scanner.components.base import never_fall


class ScannerAbsolute(threading.Thread):
    """
    ScannerAbsolute launches a scanner of the appropriate type
    depending on the network and calls the resulting handler.
    """

    def __init__(
        self,
        network: object,
        handler: object,
        contracts: object = None,
        preload_contracts: bool = False,
    ) -> None:
        super().__init__()
        self.network = network
        self.handler = handler
        self.contracts = contracts
        self.preload_contracts = preload_contracts

    def run(self):
        self.start_polling()

    @property
    def block_name(self) -> str:
        return f"{self.handler.TYPE}_{self.network.name}"

    @never_fall
    def start_polling(self) -> None:
        while True:
            scanner = Scanner(self.network, self.contracts)
            last_checked_block = scanner.get_last_block(self.block_name)
            last_network_block = scanner.get_last_network_block()

            if not last_checked_block or not last_network_block:
                scanner.sleep()
                continue

            if last_network_block - last_checked_block < 8:
                scanner.sleep()
                continue

            # filter cannot support more than 5000 blocks at one query
            if last_network_block - last_checked_block > 5000:
                last_network_block = last_checked_block + 4990

            handler = self.handler(self.network, scanner)
            handler.logger.info(f'last checked block: {last_checked_block}, last network block: {last_network_block}')

            if self.preload_contracts:
                self.contracts = getattr(scanner, f'preload_contracts_{handler.TYPE}')(self.network)
                handler.logger.info(f'Dymanic contract list items: {len(self.contracts)} items, {self.contracts}')

            event_list = getattr(scanner, f"get_events_{handler.TYPE}")(
                last_checked_block,
                last_network_block,
            )

            if event_list:
                list(map(handler.save_event, event_list))
            scanner.save_last_block(self.block_name, last_network_block)
            scanner.sleep()


