# rainbow_des/rainbow/generator_chain.py

import logging
from Crypto.Cipher import DES
from .reduction import reduce_hash

logger = logging.getLogger(__name__)

def des_hash(password: str) -> bytes:
    """
    Funkcja tworząca 64-bitowy hash z hasła przy użyciu algorytmu DES (ECB).
    Uwaga: używamy stałego klucza i szyfrujemy hasło.
    """
    try:
        if len(password) == 0:
            raise ValueError("Password cannot be empty.")

        key = b'RAINBOW1'
        cipher = DES.new(key, DES.MODE_ECB)
        padded_password = password.ljust(8, '\x00')[:8].encode('utf-8')

        result = cipher.encrypt(padded_password)
        logger.debug(f"[des_hash] password='{password}' → hash={result.hex()}")
        return result

    except Exception as e:
        logger.exception(f"[des_hash] Error processing password '{password}': {e}")
        raise


def generate_chain(start_pwd: str, pwd_length: int, chain_length: int) -> tuple[str, str]:
    """
    Generuje jeden łańcuch tęczowy:
    start_pwd → hash → reduce → hash → ... → end_pwd
    """
    try:
        if len(start_pwd) > pwd_length:
            raise ValueError(f"Start password '{start_pwd}' exceeds expected length {pwd_length}.")
        if pwd_length <= 0 or chain_length <= 0:
            raise ValueError("Password and chain lengths must be greater than zero.")

        pwd = start_pwd

        for i in range(chain_length):
            h = des_hash(pwd)
            pwd = reduce_hash(h, i, pwd_length)
            logger.debug(f"[generate_chain] Step {i}: hash={h.hex()} → pwd='{pwd}'")

        logger.info(f"[generate_chain] Chain: {start_pwd} → {pwd}")
        return start_pwd, pwd

    except Exception as e:
        logger.exception(f"[generate_chain] Error generating chain from '{start_pwd}': {e}")
        raise