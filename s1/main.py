import os, hashlib

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def file_hash(path):
    with open(path, "rb") as f:
        return sha256(f.read())

def merkle_layer(hashes):
    if len(hashes) % 2:
        hashes.append(hashes[-1])
    return [
        sha256(bytes.fromhex(hashes[i]) + bytes.fromhex(hashes[i+1]))
        for i in range(0, len(hashes), 2)
    ]

def build_tree(files):
    layer = [file_hash(f) for f in files]
    tree = [layer]
    while len(layer) > 1:
        layer = merkle_layer(layer.copy())
        tree.append(layer)
    return tree

folder = "sample_files"
files = sorted(os.path.join(folder, f) for f in os.listdir(folder)
               if f.endswith(".txt"))

tree = build_tree(files)
print("Merkle Root:", tree[-1][0])
