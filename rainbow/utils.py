import csv

def save_table_to_csv(table: list[tuple[str, str]], filepath: str) -> None:
    """
    Zapisuje tablicę tęczową do pliku CSV.

    Argumenty:
    - table: lista krotek (start_pwd, end_pwd)
    - filepath: ścieżka do pliku CSV
    """
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["start_password", "end_password"])  # nagłówek
        writer.writerows(table)
