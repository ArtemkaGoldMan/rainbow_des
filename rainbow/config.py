"""
Plik konfiguracyjny dla implementacji tablicy tęczowej DES.
Zawiera stałe, ustawienia i definicje typów.
"""

from typing import Final, List, Tuple, Iterator
import string

# Ustawienia haseł
MIN_PASSWORD_LENGTH: Final[int] = 1
MAX_PASSWORD_LENGTH: Final[int] = 8
DEFAULT_PASSWORD_LENGTH: Final[int] = 3
PASSWORD_ALPHABET: Final[str] = string.ascii_lowercase + string.digits

# Ustawienia DES
DES_KEY: Final[bytes] = b'RAINBOW1'
DES_BLOCK_SIZE: Final[int] = 8  # 64 bity

# Ustawienia generowania tablicy
DEFAULT_BATCH_SIZE: Final[int] = 10000
DEFAULT_CHAIN_LENGTH: Final[int] = 1000
DEFAULT_NUM_CHAINS: Final[int] = 1000000

# Ustawienia puli procesów
DEFAULT_TIMEOUT: Final[int] = 3600  # 1 godzina w sekundach
MIN_PROCESSES: Final[int] = 1
MAX_PROCESSES: Final[int] = 16  # Rozsądny limit dla większości systemów

# Ustawienia plików
CSV_HEADERS: Final[List[str]] = ['hasło_startowe', 'hasło_końcowe']
MAX_FILE_SIZE: Final[int] = 1024 * 1024 * 1024  # 1GB

# Definicje typów
Password = str
Hash = bytes
Chain = Tuple[Password, Password]
Table = Iterator[Chain]

# Ustawienia logowania
LOG_FORMAT: Final[str] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL: Final[str] = 'INFO'
LOG_FILE: Final[str] = 'rainbow_des.log'
MAX_LOG_SIZE: Final[int] = 1024 * 1024  # 1MB
MAX_LOG_FILES: Final[int] = 5 