import hashlib
import json
import time


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

    def mine_block(self):
        nonce = 0
        while True:
            hash_val = self.compute_hash(nonce)
            if hash_val.startswith("0000"):
                return nonce, hash_val
            nonce += 1


class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, ["Genesis Block"], "0")
        self.chain.append(genesis_block)

    def add_transaction(self, sender, receiver, amount):
        self.pending_transactions.append(
            {"sender": sender, "receiver": receiver, "amount": amount}
        )

    def add_block(self):
        new_block = Block(
            len(self.chain), self.pending_transactions, self.chain[-1].hash
        )
        self.chain.append(new_block)
        self.pending_transactions = []


# Example Run
if __name__ == "__main__":
    bchain = Blockchain()
    bchain.add_transaction("Alice", "Bob", 50)
    bchain.add_block()
    bchain.add_transaction("Charlie", "David", 20)
    bchain.add_block()
    for blk in bchain.chain:
        print(f"Block {blk.index} | Hash: {blk.hash} | Nonce: {blk.nonce}")
    print("\n=== Code Execution Successful ===")
