# Rainbow DES - Implementacja Równoległego Wyznaczania Tablic Tęczowych

## Opis Projektu
Projekt implementuje równoległe wyznaczanie tablic tęczowych do łamania haseł szyfrowanych algorytmem DES. System wykorzystuje technikę tablic tęczowych do efektywnego łamania haseł, z możliwością równoległego przetwarzania w celu przyspieszenia generowania tablic.

## Wymagania
- Python 3.6+
- Biblioteka `pycryptodome` do implementacji algorytmu DES

## Instalacja
```bash
pip install -r requirements.txt
```

## Struktura Projektu
```
rainbow_des/
├── rainbow/
│   ├── __init__.py
│   ├── crack_hash.py      # Implementacja łamania hasha
│   ├── generator_chain.py # Generowanie łańcuchów tęczowych
│   ├── reduction.py       # Funkcja redukcji
│   ├── table_builder.py   # Budowanie tablicy tęczowej
│   └── utils.py          # Funkcje pomocnicze
├── scripts/
│   ├── des_tool.py       # Główny skrypt CLI
│   ├── crack_hash_cli.py # Skrypt do łamania hasha
│   └── generate_table.py # Skrypt do generowania tablicy
├── tests/
│   ├── test_generator.py
│   ├── test_reduction.py
│   ├── test_table_builder.py
│   └── test_utils.py
└── README.md
```

## Użycie

### 1. Generowanie Hasza
```bash
python scripts/des_tool.py hash --password "hasło" --length 3
```
Parametry:
- `--password`: Hasło do zahashowania
- `--length`: Długość hasła (domyślnie 3)

### 2. Generowanie Tablicy Tęczowej
```bash
python scripts/des_tool.py generate --chains 1000000 --length 3 --chain-length 1000 --procs 8 --output rainbow_table.csv
```
Parametry:
- `--chains`: Liczba łańcuchów do wygenerowania
- `--length`: Długość hasła (musi być taka sama jak przy generowaniu hasha)
- `--chain-length`: Długość każdego łańcucha
- `--procs`: Liczba procesów do równoległego przetwarzania
- `--output`: Plik wyjściowy dla tablicy tęczowej

### 3. Łamanie Hasza
```bash
python scripts/des_tool.py crack --hash <hash> --table rainbow_table.csv --length 3 --chain-length 1000
```
Parametry:
- `--hash`: Hash do złamania (w formacie hex)
- `--table`: Ścieżka do pliku z tablicą tęczową
- `--length`: Długość hasła (musi być taka sama jak przy generowaniu tablicy)
- `--chain-length`: Długość łańcucha (musi być taka sama jak przy generowaniu tablicy)

## Przykład Pełnego Użycia

1. Generowanie hasza dla hasła "tst":
```bash
python scripts/des_tool.py hash --password "tst" --length 3
```

2. Generowanie tablicy tęczowej:
```bash
python scripts/des_tool.py generate --chains 1000000 --length 3 --chain-length 1000 --procs 8 --output rainbow_table.csv
```

3. Łamanie wygenerowanego hasza:
```bash
python scripts/des_tool.py crack --hash <wygenerowany_hash> --table rainbow_table.csv --length 3 --chain-length 1000
```

## Ważne Uwagi
- Długość hasła (`--length`) musi być taka sama we wszystkich komendach
- Długość łańcucha (`--chain-length`) musi być taka sama przy generowaniu tablicy i łamaniu hasha
- Hash musi być w formacie hex (16 znaków)
- System automatycznie weryfikuje znalezione hasło
- Równoległe przetwarzanie znacząco przyspiesza generowanie tablic

## Szczegóły Implementacji

### Algorytm DES
- Implementacja wykorzystuje standardowy algorytm DES
- Hasła są automatycznie dopełniane do 8 bajtów
- Hash jest generowany przez szyfrowanie hasła stałym kluczem

### Tablice Tęczowe
- Każdy łańcuch zaczyna się od losowego hasła
- Funkcja redukcji mapuje hashe na hasła
- Długość łańcucha jest konfigurowalna
- Wykorzystanie równoległego przetwarzania do generowania tablic

### Funkcja Redukcji
- Konwertuje hash na hasło o określonej długości
- Wykorzystuje alfabet małych liter i cyfr
- Uwzględnia indeks rundy do uniknięcia cykli

## Testy
Projekt zawiera zestaw testów jednostkowych w katalogu `tests/`. Aby uruchomić testy:
```bash
python -m pytest tests/
```

## Licencja
MIT