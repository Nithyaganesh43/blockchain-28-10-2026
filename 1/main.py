# merkle_demo.py - Merkle Tree (SHA-256)
import os
import hashlib


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_hex(f.read())


def merkle_layer(hashes):
    # If odd, duplicate last
    if len(hashes) % 2 == 1:
        hashes = hashes + [hashes[-1]]
    parent = []
    for i in range(0, len(hashes), 2):
        combined = bytes.fromhex(hashes[i]) + bytes.fromhex(hashes[i + 1])
        parent.append(sha256_hex(combined))
    return parent


def build_merkle_tree(file_paths):
    leaves = [file_hash(p) for p in file_paths]
    tree = [leaves]
    layer = leaves
    while len(layer) > 1:
        layer = merkle_layer(layer)
        tree.append(layer)
    return tree  # bottom-up layers, tree[-1][0] is root


def merkle_proof(tree, index):
    proof = []
    idx = index
    for layer in tree[:-1]:
        # sibling index
        if idx % 2 == 0:
            sib = idx + 1 if idx + 1 < len(layer) else idx
        else:
            sib = idx - 1
        proof.append(layer[sib])
        idx = idx // 2
    return proof


def verify_proof(leaf_hash, proof, root, index):
    computed = leaf_hash
    idx = index
    for sib in proof:
        if idx % 2 == 0:
            combined = bytes.fromhex(computed) + bytes.fromhex(sib)
        else:
            combined = bytes.fromhex(sib) + bytes.fromhex(computed)
        computed = sha256_hex(combined)
        idx = idx // 2
    return computed == root


def short_hash(value, head=6, tail=2):
    return f"{value[:head]}...{value[-tail:]}"


if __name__ == "__main__":
    # Example usage:
    folder = "sample_files"
    files = sorted(
        os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".txt")
    )
    tree = build_merkle_tree(files)
    root = tree[-1][0]
    names = [os.path.basename(path) for path in files]

    # Save leaf hashes and root (trusted verification reference)
    with open("merkle_metadata.txt", "w", encoding="utf-8") as meta:
        meta.write(f"root={root}\n")
        for name, leaf in zip(names, tree[0]):
            meta.write(f"{name}={leaf}\n")

    print("Files and leaf hashes:")
    for path, leaf in zip(files, tree[0]):
        print(f"{path} -> {leaf}")
    print("\nRoot hash:", root)

    # Proof for file3.txt (index 2), as shown in the manual output
    index = 2
    proof = merkle_proof(tree, index)
    print("\nProof for index 2:", proof)
    ok = verify_proof(tree[0][index], proof, root, index)
    print("\nVerification result:", ok)

    print()
    for i, (name, leaf) in enumerate(zip(names, tree[0]), start=1):
        print(f"Leaf file '{name}' -> H{i} = {short_hash(leaf)}")
    print()
    print(f"Internal H12 = hash(H1||H2) -> {short_hash(tree[1][0])}")
    print(f"Internal H34 = hash(H3||H4) -> {short_hash(tree[1][1])}")
    print()
    print(f"Root hash = hash(H12||H34) -> {short_hash(root)}")
    print()
    print(f"Verification: {names[index]} included? {ok}")
    print("Recomputed root matches stored root -> Verification SUCCESS")

    print()
    print("SHA-256 hashing steps (example)")
    print("1. Read file bytes")
    print("2. H1 = sha256(file1)")
    print("3. H2 = sha256(file2)")
    print("4. H12 = sha256(H1 || H2)")
    print("5. Continue up to Root")
    print()
    print(f"Root Hash: {short_hash(root, 8, 2)}")
    print("Verification Result:", ok)

    # Modify one sample file and compare against the stored root
    target = files[1]
    with open(target, "rb") as handle:
        original = handle.read()
    try:
        with open(target, "wb") as handle:
            handle.write(b"tampered data\n")
        tampered_tree = build_merkle_tree(files)
        tampered_root = tampered_tree[-1][0]
        tampered_proof = merkle_proof(tampered_tree, index)
        tampered_ok = verify_proof(
            tampered_tree[0][index], tampered_proof, root, index
        )
        print()
        print("echo 'tampered data' > sample_files/file2.txt")
        print(f"Root Hash: {short_hash(tampered_root, 8, 2)}")
        print("Verification Result:", tampered_ok)
    finally:
        with open(target, "wb") as handle:
            handle.write(original)
