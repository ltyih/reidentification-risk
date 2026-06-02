"""Compute k-anonymity for a CSV dataset.

Usage:
    python compute_k_anonymity.py --csv data.csv --columns age,sex,zip_code

If any provided column does not exist, the script prints k=0.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def compute_k_anonymity(rows: list[dict], columns: list[str]) -> int:
    if not rows:
        return 0

    header = list(rows[0].keys())
    missing = [col for col in columns if col not in header]
    if missing:
        for col in missing:
            print(f"{col} not found")
        return 0

    groups: dict[tuple, int] = {}
    for row in rows:
        key = tuple(row[col] for col in columns)
        groups[key] = groups.get(key, 0) + 1

    return min(groups.values()) if groups else 0


def load_csv(path: Path) -> list[dict]:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except UnicodeDecodeError:
        with path.open(newline="", encoding="cp936", errors="replace") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute k-anonymity for a CSV dataset.")
    parser.add_argument("--csv", dest="csv_path", required=True, help="Path to the CSV file")
    parser.add_argument(
        "--columns",
        required=True,
        help="Comma-separated list of column names to use as quasi-identifiers",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        print(f"Error: file does not exist: {csv_path}", file=sys.stderr)
        sys.exit(1)

    columns = [col.strip() for col in args.columns.split(",") if col.strip()]
    if not columns:
        print("Error: at least one column name is required", file=sys.stderr)
        sys.exit(1)

    rows = load_csv(csv_path)
    k = compute_k_anonymity(rows, columns)
    print(k)


if __name__ == "__main__":
    main()
