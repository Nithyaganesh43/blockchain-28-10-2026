import hashlib
import json
import time
import random


class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce, self.hash = self.mine_block()

    def compute_hash(self, nonce):
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": self.transactions,
                "previous_hash": self.previous_hash,
                "nonce": nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty="000"):
        nonce = 0
        while True:
            hash_val = self.compute_hash(nonce)
            if hash_val.startswith(difficulty):
                return nonce, hash_val
            nonce += 1


# ---------- Blockchain Definition ----------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, ["Genesis Block"], "0" * 64)
        self.chain.append(genesis)

    def add_block(self, transactions):
        prev_hash = self.chain[-1].hash
        block = Block(len(self.chain), transactions, prev_hash)
        self.chain.append(block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            prev, curr = self.chain[i - 1], self.chain[i]
            if curr.previous_hash != prev.hash:
                return False
            if curr.hash != curr.compute_hash(curr.nonce):
                return False
        return True


# ---------- Consensus Function ----------
def consensus(chains):
    longest_chain = None
    max_len = 0
    for chain in chains:
        if chain.is_valid() and len(chain.chain) > max_len:
            longest_chain = chain.chain
            max_len = len(chain.chain)
    # Replace all other chains
    for bc in chains:
        bc.chain = list(longest_chain)
    return longest_chain


# ---------- Demonstration ----------
if __name__ == "__main__":
    # Simulate three nodes
    node1, node2, node3 = Blockchain(), Blockchain(), Blockchain()
    # Each node mines different transactions
    node1.add_block(["A pays B 5"])
    node1.add_block(["C pays D 7"])
    node2.add_block(["X pays Y 10"])
    node3.add_block(["M pays N 2", "N pays O 4"])
    print("\nBefore Consensus:")
    for i, n in enumerate([node1, node2, node3], start=1):
        print(f"Node {i} chain length: {len(n.chain)}")
    # Run consensus algorithm
    consensus([node1, node2, node3])
    print("\nAfter Consensus:")
    for i, n in enumerate([node1, node2, node3], start=1):
        print(f"Node {i} chain length: {len(n.chain)}")
    print("\nConsensus achieved – all nodes synchronized.")
    print("\n=== Code Execution Successful ===")
