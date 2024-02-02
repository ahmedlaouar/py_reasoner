import random

MIN_PER_RANK = 1  # Nodes/Rank: How 'fat' the DAG should be.
MAX_PER_RANK = 5
MIN_RANKS = 3     # Ranks: How 'tall' the DAG should be.
MAX_RANKS = 5
PERCENT = 30      # Chance of having an Edge.

def main():
    nodes = 0
    random.seed()  # Initialize the random number generator
    ranks = MIN_RANKS + random.randint(0, MAX_RANKS - MIN_RANKS)

    print("digraph {")
    for i in range(ranks):
        # New nodes of 'higher' rank than all nodes generated till now.
        new_nodes = MIN_PER_RANK + random.randint(0, MAX_PER_RANK - MIN_PER_RANK)
        # Edges from old nodes ('nodes') to new ones ('new_nodes').
        for j in range(nodes):
            for k in range(new_nodes):
                if random.randint(0, 99) < PERCENT:
                    print(f"  {j} -> {k + nodes};")  # An Edge.
        nodes += new_nodes  # Accumulate into old node set.
    print("}")

if __name__ == "__main__":
    main()
