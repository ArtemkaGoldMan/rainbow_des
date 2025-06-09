import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rainbow.generator_chain import des_hash
from rainbow.reduction import reduce_hash

def test_uniqueness_of_reduction():
    pwd_length = 8
    seen = set()
    for i in range(100_0000):
        h = des_hash(f"x{i}")
        p = reduce_hash(h, i, pwd_length)
        seen.add(p)
    unique_count = len(seen)
    print(f"Unique passwords after {pwd_length} steps: {unique_count}")
    assert unique_count > 90_000

