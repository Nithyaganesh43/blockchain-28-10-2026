import time
import json
import hashlib
from typing import List, Optional, Dict, Any
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_merkle_root(transactions: List[str]) -> str:
    if not transactions:
        # Conventional choice: hash of empty string
        return sha256_hex(b"")

    # Start with leaf hashes
    layer = [sha256_hex(tx.encode()) for tx in transactions]

    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        parent = []
        for i in range(0, len(layer), 2):
            combined = bytes.fromhex(layer[i]) + bytes.fromhex(layer[i + 1])
            parent.append(sha256_hex(combined))
        layer = parent
    return layer[0]


class Block:
    def __init__(
        self,
        index: int,
        transactions: List[str],
        previous_hash: str,
        signer_pubkey_hex: Optional[str] = None,
    ):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions.copy()
        self.previous_hash = previous_hash
        self.merkle_root = compute_merkle_root(self.transactions)
        self.nonce = 0
        self.signature: Optional[str] = None  # hex string
        self.signer_pubkey_hex = signer_pubkey_hex

    def header_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": round(self.timestamp, 6),  # rounded for deterministic representation
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
        }

    def compute_header_hash(self) -> str:
        header_json = json.dumps(
            self.header_dict(), sort_keys=True, separators=(",", ":")
        )
        return sha256_hex(header_json.encode())

    def sign_block(self, signing_key: SigningKey):
        header_hash = self.compute_header_hash()
        sig_bytes = signing_key.sign(header_hash.encode())
        self.signature = sig_bytes.hex()
        self.signer_pubkey_hex = (
            signing_key.get_verifying_key().to_string("compressed").hex()
        )

    def verify_signature(self) -> bool:
        if not (self.signature and self.signer_pubkey_hex):
            return False
        try:
            vk_bytes = bytes.fromhex(self.signer_pubkey_hex)
            vk = VerifyingKey.from_string(
                vk_bytes, curve=SECP256k1, hashfunc=hashlib.sha256
            )
            header_hash = self.compute_header_hash()
            return vk.verify(bytes.fromhex(self.signature), header_hash.encode())
        except (BadSignatureError, Exception):
            return False

    def mine(self, difficulty_prefix: str = "0000", max_attempts: int = 5_000_000):
        attempts = 0
        while attempts < max_attempts:
            h = self.compute_header_hash()
            if h.startswith(difficulty_prefix):
                return True
            self.nonce += 1
            attempts += 1
        return False


class Blockchain:
    def __init__(self, difficulty_prefix: str = "0000"):
        self.chain: List[Block] = []
        self.difficulty_prefix = difficulty_prefix
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(
            index=0, transactions=["Genesis Block"], previous_hash="0" * 64
        )
        self.chain.append(genesis)

    def last_hash(self) -> str:
        return self.chain[-1].compute_header_hash()

    def add_block(
        self, transactions: List[str], signing_key: SigningKey, do_mine: bool = True
    ) -> Block:
        new_block = Block(
            index=len(self.chain),
            transactions=transactions,
            previous_hash=self.last_hash(),
        )
        # optional mining to satisfy difficulty
        if do_mine and self.difficulty_prefix:
            mined = new_block.mine(self.difficulty_prefix)
            if not mined:
                raise RuntimeError("Failed to mine block")
        new_block.sign_block(signing_key)
        self.chain.append(new_block)
        return new_block

    def validate_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            prev_block = self.chain[i - 1]
            block = self.chain[i]
            # 1) check previous hash linkage
            expected_prev_hash = prev_block.compute_header_hash()
            if block.previous_hash != expected_prev_hash:
                print(f"Invalid previous_hash at block {block.index}")
                return False
            # 2) check merkle root
            recomputed_merkle = compute_merkle_root(block.transactions)
            if recomputed_merkle != block.merkle_root:
                print(f"Merkle root mismatch at block {block.index}")
                return False
            # 3) check signature
            if not block.verify_signature():
                print(f"Signature verification failed at block {block.index}")
                return False
        # verify genesis signature if present
        if len(self.chain) > 0:
            if self.chain[0].signature and not self.chain[0].verify_signature():
                print("Genesis signature invalid")
                return False
        return True


if __name__ == "__main__":
    # 1) generate ECDSA keypair (signer)
    # hashfunc must match verify_signature(), which uses SHA-256
    sk = SigningKey.generate(curve=SECP256k1, hashfunc=hashlib.sha256)
    vk = sk.get_verifying_key()
    print(
        "Signer public key (compressed hex):",
        vk.to_string("compressed").hex()[:64],
        "...",
    )

    bc = Blockchain(difficulty_prefix="000")
    bc.chain[0].mine(bc.difficulty_prefix)
    bc.chain[0].sign_block(sk)
    print("Genesis header hash:", bc.chain[0].compute_header_hash())
    print(
        "Genesis signature (truncated):",
        (bc.chain[0].signature or "")[:64],
        "...",
    )

    txs_block1 = ["Alice pays Bob 10", "Bob pays Carol 3"]
    b1 = bc.add_block(txs_block1, signing_key=sk, do_mine=True)
    print(
        f"Added Block {b1.index} | Header Hash: {b1.compute_header_hash()} | Nonce: {b1.nonce}"
    )
    print("Block 1 Merkle Root:", b1.merkle_root)
    print("Block 1 signature (truncated):", b1.signature[:64], "...")

    txs_block2 = ["Dave pays Erin 7"]
    b2 = bc.add_block(txs_block2, signing_key=sk, do_mine=True)
    print(
        f"Added Block {b2.index} | Header Hash: {b2.compute_header_hash()} | Nonce: {b2.nonce}"
    )
    print("Block 2 Merkle Root:", b2.merkle_root)

    print("\n=== Blockchain Data ===")
    for block in bc.chain:
        print(f"\nBlock {block.index}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Merkle Root: {block.merkle_root}")
        print(f"Nonce: {block.nonce}")
        print(f"Hash: {block.compute_header_hash()}")
        print(f"Prev Hash: {block.previous_hash[:20]} ...")

    valid = bc.validate_chain()
    print("\nBlockchain valid:", valid)
    print("Chain validation result:", valid)

    print("\n--- Tamper Test ---")
    print("-- Tamper test: modify transaction in Block 1 --")
    bc.chain[1].transactions[0] = "Alice pays Bob 9999"  # tamper
    bc.chain[1].merkle_root = compute_merkle_root(bc.chain[1].transactions)
    valid_after_tamper = bc.validate_chain()
    print("Blockchain valid after tamper:", valid_after_tamper)
    print("Chain validation after tamper (should be False):", valid_after_tamper)
