from pytest import raises
from eth_tester.exceptions import TransactionFailed
from constants import *


def test_deposits(w3, tester, pp):
    DEPOSIT_VALUE = 555
    for account in w3.eth.accounts:
        # tx_hash = pp.deposit(transact={'from': account, 'value': DEPOSIT_VALUE})
        # tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        pp.deposit(transact={'from': account, 'value': DEPOSIT_VALUE})
        assert pp.deposits(account) == DEPOSIT_VALUE
    assert pp.total_deposits() == DEPOSIT_VALUE * len(w3.eth.accounts)
