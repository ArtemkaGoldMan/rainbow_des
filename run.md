1. python scripts/des_tool.py hash --password "a1с" --length 3
2. python scripts/des_tool.py generate --chains 100000 --length 3 --chain-length 100 --procs 8 --batch-size 1000 --seed 42 --output rainbow_table.csv
3-1. python scripts/des_tool.py crack --hash <hash_from_step_1> --table rainbow_table.csv --length 3 --chain-length 100
3-2. python scripts/des_tool.py crack --hash-file hashes.txt --table rainbow_table.csv --length 6 --chain-length 100
