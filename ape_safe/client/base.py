from abc import ABC, abstractmethod
from typing import Dict, Iterator, Optional, Set, Union

from ape.types import AddressType, MessageSignature

from ape_safe.client.models import (
    ExecutedTxData,
    SafeApiTxData,
    SafeDetails,
    SafeTx,
    SafeTxConfirmation,
    SafeTxID,
    UnexecutedTxData,
)


class BaseSafeClient(ABC):
    @property
    @abstractmethod
    def safe_details(self) -> SafeDetails:
        ...

    @abstractmethod
    def get_next_nonce(self) -> int:
        ...

    @abstractmethod
    def _all_transactions(self) -> Iterator[SafeApiTxData]:
        ...

    def get_transactions(
        self,
        confirmed: Optional[bool] = None,
        starting_nonce: int = 0,
        filter_by_ids: Optional[Set[SafeTxID]] = None,
        filter_by_missing_signers: Optional[Set[AddressType]] = None,
    ) -> Iterator[SafeApiTxData]:
        """
        confirmed: Confirmed if True, not confirmed if False, both if None
        """
        next_nonce = self.get_next_nonce()

        for txn in self._all_transactions():
            if txn.nonce < starting_nonce:
                break  # NOTE: order is largest nonce to smallest, so safe to break here

            is_confirmed = len(txn.confirmations) >= txn.confirmations_required

            if confirmed is not None:
                if not confirmed and isinstance(txn, ExecutedTxData):
                    break  # NOTE: Break at the first executed transaction

                elif confirmed and not is_confirmed:
                    continue  # NOTE: Skip not confirmed transactions

            if txn.nonce < next_nonce and isinstance(txn, UnexecutedTxData):
                continue  # NOTE: Skip orphaned transactions

            if filter_by_ids and txn.safe_tx_hash not in filter_by_ids:
                continue  # NOTE: Skip transactions not in the filter

            if filter_by_missing_signers and filter_by_missing_signers.issubset(
                set(conf.owner for conf in txn.confirmations)
            ):
                # NOTE: Skip if all signers from `filter_by_missing_signers`
                #       are in `txn.confirmations`
                continue

            yield txn

    @abstractmethod
    def get_confirmations(self, safe_tx_hash: SafeTxID) -> Iterator[SafeTxConfirmation]:
        ...

    @abstractmethod
    def post_transaction(self, safe_tx: SafeTx, sigs: Dict[AddressType, MessageSignature]):
        ...

    @abstractmethod
    def post_signature(
        self,
        safe_tx_or_hash: Union[SafeTx, SafeTxID],
        signer: AddressType,
        signature: MessageSignature,
    ):
        ...
