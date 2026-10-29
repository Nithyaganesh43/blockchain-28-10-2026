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
            if h.startswith("0000"):
                return nonce, h
            nonce += 1


class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append(Block(0, ["Genesis Block"], "0"))

    def add_transaction(self, sender, receiver, amount):
        self.pending_transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })

    def add_block(self):
        block = Block(
            len(self.chain),
            self.pending_transactions,
            self.chain[-1].hash
        )
        self.chain.append(block)
        self.pending_transactions = []


bc = Blockchain()
bc.add_transaction("Alice", "Bob", 50)
bc.add_block()
bc.add_transaction("Charlie", "David", 20)
bc.add_block()

for block in bc.chain:
    print(f"Block {block.index} | Hash: {block.hash} | Nonce: {block.nonce}")
