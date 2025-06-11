"""
Configuration file for DES rainbow table implementation.
Contains constants, settings, and type definitions.
"""

from typing import Final, List, Tuple, Iterator
import string

# Password settings
MIN_PASSWORD_LENGTH: Final[int] = 1
MAX_PASSWORD_LENGTH: Final[int] = 8
DEFAULT_PASSWORD_LENGTH: Final[int] = 3
PASSWORD_ALPHABET: Final[str] = string.ascii_lowercase + string.digits

# DES settings
DES_KEY: Final[bytes] = b'RAINBOW1'
DES_BLOCK_SIZE: Final[int] = 8  # 64 bits

# Table generation settings
DEFAULT_BATCH_SIZE: Final[int] = 10000
DEFAULT_CHAIN_LENGTH: Final[int] = 1000
DEFAULT_NUM_CHAINS: Final[int] = 1000000

# Process pool settings
DEFAULT_TIMEOUT: Final[int] = 3600  # 1 hour in seconds
MIN_PROCESSES: Final[int] = 1
MAX_PROCESSES: Final[int] = 16  # Reasonable limit for most systems

# File settings
CSV_HEADERS: Final[List[str]] = ['start_password', 'end_password']
MAX_FILE_SIZE: Final[int] = 1024 * 1024 * 1024  # 1GB

# Type definitions
Password = str
Hash = bytes
Chain = Tuple[Password, Password]
Table = Iterator[Chain] 