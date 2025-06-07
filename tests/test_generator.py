from rainbow.generator_chain import generate_chain

def test_generate_chain_returns_correct_format():
    start_pwd = "abc123"
    start, end = generate_chain(start_pwd, pwd_length=6, chain_length=10)

    assert start == start_pwd
    assert isinstance(end, str)
    assert len(end) == 6
    assert start != end  # przy łańcuchu długości > 0 wynik powinien być inny
