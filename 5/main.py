import secrets
import hashlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def create_wallet():
    private_key = secrets.token_hex(32)
    public_key = hashlib.sha256(private_key.encode()).hexdigest()
    return private_key, public_key


ledger = {}


def get_balance(address):
    return ledger.get(address, 0)


def send_funds(sender, receiver, amount):
    if ledger.get(sender, 0) < amount:
        print("Insufficient balance.")
        return False
    ledger[sender] -= amount
    ledger[receiver] = ledger.get(receiver, 0) + amount
    print(f"Transaction: {sender[:10]} → {receiver[:10]} | Amount: {amount}")
    return True


if __name__ == "__main__":
    print("=== Decentralized Wallet Demo ===")
    privA, addrA = create_wallet()
    privB, addrB = create_wallet()
    ledger[addrA] = 100  # initial balance for demo
    print(f"\nWallet A Address: {addrA}\nPrivate Key: {privA[:20]}...")
    print(f"Wallet B Address: {addrB}\nPrivate Key: {privB[:20]}...")
    print("\nInitial Balances:")
    print("A:", get_balance(addrA))
    print("B:", get_balance(addrB))
    send_funds(addrA, addrB, 40)
    print("\nUpdated Balances:")
    print("A:", get_balance(addrA))
    print("B:", get_balance(addrB))
    print("\n=== Code Execution Successful ===")
