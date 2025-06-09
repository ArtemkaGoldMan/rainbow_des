import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rainbow.generator_chain import des_hash
from rainbow.reduction import reduce_hash
from multiprocessing import Pool, cpu_count


def process_chain(i):
    pwd_length = 6
    chain_length = 100
    pwd = f"{i:06}"  
    current = pwd

    for j in range(chain_length):
        h = des_hash(current)
        current = reduce_hash(h, j, pwd_length)

    return current


def test_full_chain_uniqueness_parallel():
    num_chains = 100_000 
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_chain, range(num_chains))

    unique_count = len(set(results))
    print(f"\nUnique passwords after 100 steps with {num_chains} chains: {unique_count}")
    assert unique_count > num_chains * 0.9
