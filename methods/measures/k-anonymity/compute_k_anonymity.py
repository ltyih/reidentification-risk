"""Compute k-anonymity for a CSV dataset.

Usage:
    # Show only k value for all columns
    python compute_k_anonymity.py --csv data.csv
    
    # Show only k value for specific columns
    python compute_k_anonymity.py --csv data.csv --columns age,sex,zip_code
    
    # Show top 5 smallest groups
    python compute_k_anonymity.py --csv data.csv --columns age,sex,zip_code --top-k 5
    
    # Show all combinations
    python compute_k_anonymity.py --csv data.csv --show-all
    
    # Save results to CSV
    python compute_k_anonymity.py --csv data.csv --show-all --output-csv results.csv

If any provided column does not exist, the script prints "{column} not found".
If --columns is not provided, all columns in the CSV are used.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def compute_k_anonymity(rows: list[dict], columns: list[str]) -> tuple[int, dict[tuple, int]]:
    if not rows:
        return 0, {}

    header = list(rows[0].keys())
    missing = [col for col in columns if col not in header]
    if missing:
        for col in missing:
            print(f"{col} not found")
        return 0, {}

    groups: dict[tuple, int] = {}
    for row in rows:
        key = tuple(row[col] for col in columns)
        groups[key] = groups.get(key, 0) + 1

    k = min(groups.values()) if groups else 0
    return k, groups


def load_csv(path: Path) -> list[dict]:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except UnicodeDecodeError:
        with path.open(newline="", encoding="cp936", errors="replace") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]


def _get_csv_columns(path: Path) -> list[str]:
    """Read and return all column names from CSV header."""
    for encoding in ("utf-8", "cp936"):
        try:
            with path.open(newline="", encoding=encoding, errors="strict") as f:
                reader = csv.DictReader(f)
                return reader.fieldnames or []
        except UnicodeDecodeError:
            continue
    return []


def compute_k_anonymity_stream(path: Path, columns: list[str]) -> tuple[int, dict[tuple, int]]:
    """Stream through a CSV file and compute group counts without loading all rows.

    Returns (k, groups) where groups maps tuples (column values) -> count.
    If any requested column is missing, prints the missing names and returns (0, {}).
    """
    # Try UTF-8 then fall back to cp936 as in load_csv
    for encoding in ("utf-8", "cp936"):
        try:
            with path.open(newline="", encoding=encoding, errors="strict") as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames or []
                missing = [col for col in columns if col not in header]
                if missing:
                    for col in missing:
                        print(f"{col} not found")
                    return 0, {}

                groups: dict[tuple, int] = {}
                for row in reader:
                    key = tuple(row.get(col, "") for col in columns)
                    groups[key] = groups.get(key, 0) + 1

                k = min(groups.values()) if groups else 0
                return k, groups
        except UnicodeDecodeError:
            # try next encoding
            continue
    # If we get here, both encodings failed -- report error
    print(f"Error: unable to decode file {path}")
    return 0, {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute k-anonymity for a CSV dataset.")
    parser.add_argument("--csv", dest="csv_path", required=True, help="Path to the CSV file")
    parser.add_argument(
        "--columns",
        required=False,
        default=None,
        help="Comma-separated list of column names. If not provided, all columns are used.",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show all combinations and their counts",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Show top N smallest groups",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=None,
        help="Save results to CSV file",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        print(f"Error: file does not exist: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Determine columns: either from user input or auto-detect from CSV header
    if args.columns:
        columns = [col.strip() for col in args.columns.split(",") if col.strip()]
        if not columns:
            print("Error: at least one column name is required", file=sys.stderr)
            sys.exit(1)
    else:
        # Auto-detect all columns from CSV header
        columns = _get_csv_columns(csv_path)
        if not columns:
            print(f"Error: unable to detect columns from {csv_path}", file=sys.stderr)
            sys.exit(1)

    # Use stream-processing to avoid loading entire file into memory
    k, groups = compute_k_anonymity_stream(csv_path, columns)
    
    if not groups:
        return

    if args.show_all:
        _output_all_groups(groups, columns, args.output_csv)
    elif args.top_k:
        _output_top_k_groups(groups, columns, args.top_k, args.output_csv)
    else:
        print(k)
        if args.output_csv:
            _save_result_to_csv(args.output_csv, [("k", k)])


def _output_all_groups(groups: dict[tuple, int], columns: list[str], output_csv: str | None) -> None:
    """Output all combinations sorted by count."""
    sorted_groups = sorted(groups.items(), key=lambda x: x[1])
    results = []
    
    for combo, count in sorted_groups:
        row = {columns[i]: combo[i] for i in range(len(columns))}
        row["count"] = count
        results.append(row)
        print(" | ".join(f"{col}={combo[i]}" for i, col in enumerate(columns)), f"count={count}")
    
    if output_csv:
        _save_results_to_csv(output_csv, results)


def _output_top_k_groups(groups: dict[tuple, int], columns: list[str], top_k: int, output_csv: str | None) -> None:
    """Output top N smallest groups."""
    sorted_groups = sorted(groups.items(), key=lambda x: x[1])[:top_k]
    results = []
    
    for combo, count in sorted_groups:
        row = {columns[i]: combo[i] for i in range(len(columns))}
        row["count"] = count
        results.append(row)
        print(" | ".join(f"{col}={combo[i]}" for i, col in enumerate(columns)), f"count={count}")
    
    if output_csv:
        _save_results_to_csv(output_csv, results)


def _save_results_to_csv(path: str, results: list[dict]) -> None:
    """Save results to CSV file."""
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            if not results:
                return
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to {path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving to CSV: {e}", file=sys.stderr)


def _save_result_to_csv(path: str, results: list[tuple]) -> None:
    """Save simple k value to CSV."""
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            writer.writerows(results)
        print(f"Results saved to {path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving to CSV: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
