import hashlib, json, time
from ecdsa import SigningKey, VerifyingKey, SECP256k1

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def merkle_root(txs):
    if not txs:
        return sha256(b"")
    layer = [sha256(tx.encode()) for tx in txs]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [sha256(bytes.fromhex(layer[i]) + bytes.fromhex(layer[i+1]))
                 for i in range(0, len(layer), 2)]
    return layer[0]

class Block:
    def __init__(self, index, txs, prev):
        self.index = index
        self.timestamp = time.time()
        self.transactions = txs
        self.previous_hash = prev
        self.merkle_root = merkle_root(txs)
        self.nonce = 0
        self.signature = None
        self.public_key = None

    def header_hash(self):
        data = json.dumps({
            "index": self.index,
            "timestamp": round(self.timestamp, 6),
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce
        }, sort_keys=True, separators=(",", ":"))
        return sha256(data.encode())

    def sign(self, sk):
        self.signature = sk.sign(self.header_hash().encode()).hex()
        self.public_key = sk.get_verifying_key().to_string("compressed").hex()

    def verify(self):
        try:
            vk = VerifyingKey.from_string(
                bytes.fromhex(self.public_key), curve=SECP256k1
            )
            return vk.verify(
                bytes.fromhex(self.signature), self.header_hash().encode()
            )
        except Exception:
            return False

class Blockchain:
    def __init__(self):
        self.chain = [Block(0, ["Genesis Block"], "0" * 64)]

    def add_block(self, txs, sk):
        b = Block(len(self.chain), txs, self.chain[-1].header_hash())
        b.sign(sk)
        self.chain.append(b)

    def validate(self):
        for i in range(1, len(self.chain)):
            b, p = self.chain[i], self.chain[i-1]
            if b.previous_hash != p.header_hash():
                return False
            if b.merkle_root != merkle_root(b.transactions):
                return False
            if not b.verify():
                return False
        return True

sk = SigningKey.generate(curve=SECP256k1)
bc = Blockchain()
bc.chain[0].sign(sk)
bc.add_block(["Alice pays Bob 10", "Bob pays Carol 3"], sk)
bc.add_block(["Dave pays Erin 7"], sk)

print("Merkle Root:", bc.chain[1].merkle_root)
print("Chain Valid:", bc.validate())

bc.chain[1].transactions[0] = "Alice pays Bob 9999"
print("After Tampering:", bc.validate())
