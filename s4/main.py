import hashlib, json, time

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce, self.hash = self.mine_block()

    def compute_hash(self, nonce):
        data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": nonce
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self):
        nonce = 0
        while True:
            h = self.compute_hash(nonce)
            if h.startswith("000"):
                return nonce, h
            nonce += 1


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append(Block(0, ["Genesis Block"], "0" * 64))

    def add_block(self, transactions):
        block = Block(len(self.chain), transactions, self.chain[-1].hash)
        self.chain.append(block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            prev, curr = self.chain[i-1], self.chain[i]
            if curr.previous_hash != prev.hash:
                return False
            if curr.hash != curr.compute_hash(curr.nonce):
                return False
        return True


def consensus(chains):
    valid = [bc for bc in chains if bc.is_valid()]
    if not valid:
        return
    longest = max(valid, key=lambda bc: len(bc.chain)).chain
    for bc in chains:
        bc.chain = list(longest)


node1, node2, node3 = Blockchain(), Blockchain(), Blockchain()

node1.add_block(["A pays B 5"])
node1.add_block(["C pays D 7"])
node2.add_block(["X pays Y 10"])
node3.add_block(["M pays N 2"])

consensus([node1, node2, node3])

for i, node in enumerate([node1, node2, node3], 1):
    print(f"Node {i} chain length: {len(node.chain)}")
    print("Valid:", node.is_valid())
