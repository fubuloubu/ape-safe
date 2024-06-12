import pytest

from ape_safe.exceptions import SafeLogicError


def test_asset(vault, token):
    assert vault.asset() == token


def test_default_operation(safe, token, vault, multisend):
    amount = token.balanceOf(safe)
    multisend.add(token.approve, vault, 123)
    multisend.add(vault.transfer, safe, amount)
    receipt = multisend(sender=safe)
    assert receipt.txn_hash


def test_no_operation(safe, token, vault, multisend):
    amount = token.balanceOf(safe)
    multisend.add(token.approve, vault, 123)
    multisend.add(vault.transfer, safe, amount)
    with pytest.raises(SafeLogicError, match="Safe transaction failed"):
        multisend(sender=safe, operation=0)


def test_decode_multisend(multisend):
    calldata = bytes.fromhex(
        "8d80ff0a0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000016b00527e80008d212e2891c737ba8a2768a7337d7fd200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000024f0080878000000000000000000000000584bffc5f51ccae39ad69f1c399743620e619c2b00da18f789a1d9ad33e891253660fcf1332d236b2900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000024e74b981b000000000000000000000000584bffc5f51ccae39ad69f1c399743620e619c2b0027b5739e22ad9033bcbf192059122d163b60349d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000247a55036500000000000000000000000000000000000000000000000000002a1b324b8f68000000000000000000000000000000000000000000"  # noqa: E501
    )
    multisend.add_from_calldata(calldata)
    assert multisend.handler.encode_input(b"".join(multisend.encoded_calls)) == calldata
