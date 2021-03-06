
from web3 import Web3
from web3.contract import ConciseContract
from eth_tester import EthereumTester, PyEVMBackend
from vyper import compiler
from math import floor, ceil, log
from hexbytes import HexBytes
from plasmalib.constants import *
# import json

from pprint import PrettyPrinter
PP = PrettyPrinter(indent=4)


class MST:
    def __init__(self, l, r):
        self.l = l
        self.r = r
        self.h = Web3.sha3(l.h + r.h)

class Leaf:
    def __init__(self, tx):
        self.tx = tx
        self.h = tx.h

class Msg:
    def __init__(self, sender, recipient, start, offset):
        self.sender = sender
        self.recipient = recipient
        self.start = start
        self.offset = offset
        self.h = Web3.sha3(
            addr_to_bytes(self.sender) +
            addr_to_bytes(self.recipient) +
            to_bytes32(self.start) +
            to_bytes32(self.offset)
        )

class Tx:
    def __init__(self, msg, signer):
        self.msg = msg
        # self.sig = signer(msg.h)
        sig = signer(msg.h)
        self.sigv = sig.v
        self.sigr = sig.r
        self.sigs = sig.s
        self.h = Web3.sha3(
            addr_to_bytes(self.msg.sender) +
            addr_to_bytes(self.msg.recipient) +
            to_bytes32(self.msg.start) +
            to_bytes32(self.msg.offset) +
            to_bytes32(self.sigv) +
            to_bytes32(self.sigr) +
            to_bytes32(self.sigs)
        )

    # def json(self):
        # return json.dumps(self, default = lambda o: o.__dict__)

class NullTx:
    def __init__(self):
        self.h = HexBytes(b'\x00' * 32)

# class Sig:
    # def __init__(self, v, r, s):
        # self.v = v
        # self.r = r
        # self.s = s

def pairs(l):
    return [(l[i], l[i + 1]) for i in range(0, len(l), 2)]

# assumes no overlapping txs
def construct_tree(txs):
    depth = ceil(log(len(txs), 2))
    assert depth <= MAX_TREE_DEPTH

    leaves = [Leaf(tx) for tx in txs]
    leaves.sort(key = lambda leaf: leaf.tx.msg.start)
    leaves += [Leaf(NullTx())] * (2 ** depth - len(leaves))

    fst = lambda x: x[0]
    snd = lambda x: x[1]
    nodes = leaves
    # depth = 1
    for i in range(depth):
        nodes = list(map(lambda x: MST(fst(x), snd(x)), pairs(nodes)))
    return nodes[0]


def addr_to_bytes(addr):
    return bytes.fromhex(addr[2:])

def to_bytes32(i):
    return i.to_bytes(32, byteorder='big')

def contract_factory(w3, source):
    bytecode = '0x' + compiler.compile(source).hex()
    abi = compiler.mk_full_signature(source)
    return w3.eth.contract(abi=abi, bytecode=bytecode)
