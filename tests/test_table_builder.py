from rainbow.table_builder import generate_table

def test_generate_table_basic():
    # Prosta lista startowych haseł
    start_passwords = ["abc001", "abc002", "abc003"]
    pwd_length = 6
    chain_length = 5
    num_procs = 2

    table = generate_table(start_passwords, pwd_length, chain_length, num_procs)

    # Sprawdźmy, że długość listy się zgadza
    assert len(table) == len(start_passwords)

    # Każdy wynik to krotka (start, end)
    for start, end in table:
        assert isinstance(start, str)
        assert isinstance(end, str)
        assert len(start) == pwd_length
        assert len(end) == pwd_length
