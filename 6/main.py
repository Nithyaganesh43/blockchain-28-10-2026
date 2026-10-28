import hashlib
import json
import time
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class VoteBlock:
    def __init__(self, voter_id, candidate, previous_hash):
        self.voter_id = voter_id
        self.candidate = candidate
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_str = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()


class VotingBlockchain:
    def __init__(self):
        self.chain = []
        self.voters = set()
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = VoteBlock("0", "Genesis", "0" * 64)
        self.chain.append(genesis)

    def add_vote(self, voter_id, candidate):
        if voter_id in self.voters:
            print(f"Duplicate vote blocked: {voter_id}")
            return
        prev_hash = self.chain[-1].hash
        new_vote = VoteBlock(voter_id, candidate, prev_hash)
        self.chain.append(new_vote)
        self.voters.add(voter_id)
        print(f"Vote added: {voter_id} → {candidate}")

    def tally_votes(self):
        results = {}
        for block in self.chain[1:]:
            results[block.candidate] = results.get(block.candidate, 0) + 1
        return results


if __name__ == "__main__":
    vb = VotingBlockchain()
    vb.add_vote("V001", "Alice")
    vb.add_vote("V002", "Bob")
    vb.add_vote("V003", "Alice")
    vb.add_vote("V001", "Alice")  # Duplicate vote attempt
    print("\nVote Tally:")
    tally = vb.tally_votes()
    for candidate, count in tally.items():
        print(f"{candidate}: {count} votes")
    print("\nBlockchain Length:", len(vb.chain))
    print("\n=== Code Execution Successful ===")
