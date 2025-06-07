import os
import csv
from rainbow.utils import save_table_to_csv

def test_save_table_to_csv(tmp_path):
    # Przykładowa tabela
    table = [("aaaaaa", "zzzzzz"), ("bbbbbb", "yyyyyy")]

    # Ścieżka do tymczasowego pliku CSV
    csv_file = tmp_path / "output.csv"

    # Zapisz tabelę
    save_table_to_csv(table, csv_file)

    # Odczytaj i sprawdź zawartość
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Spodziewane dane
    assert rows[0] == ["start_password", "end_password"]
    assert rows[1] == ["aaaaaa", "zzzzzz"]
    assert rows[2] == ["bbbbbb", "yyyyyy"]
