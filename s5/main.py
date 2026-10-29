import secrets, hashlib

def create_wallet():
    private_key = secrets.token_hex(32)
    address = hashlib.sha256(private_key.encode()).hexdigest()
    return private_key, address

ledger = {}

def get_balance(address):
    return ledger.get(address, 0)

def send_funds(sender, receiver, amount):
    if amount <= 0 or ledger.get(sender, 0) < amount:
        print("Insufficient balance or invalid amount.")
        return False

    ledger[sender] -= amount
    ledger[receiver] = ledger.get(receiver, 0) + amount
    print("Transaction successful:", amount)
    return True

privA, addrA = create_wallet()
privB, addrB = create_wallet()

ledger[addrA] = 100

print("Wallet A:", addrA)
print("Wallet B:", addrB)
print("Initial Balances:", get_balance(addrA), get_balance(addrB))

send_funds(addrA, addrB, 40)

print("Updated Balances:", get_balance(addrA), get_balance(addrB))
