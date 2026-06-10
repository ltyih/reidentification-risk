import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.special import hyp2f1

def bf_risk(f_k, p_hat):
    """
    Benedetti-Franconi individual disclosure risk
    
    Parameters:
        f_k: sample frequency of the combination (positive integer)
        p_hat: estimated sampling probability = f_k / sum(weights) (0 < p_hat <= 1)
    
    Returns:
        r_k: individual disclosure risk (between 0 and 1)
    """
    if not (isinstance(f_k, (int, float, np.integer)) and f_k == int(f_k) and f_k > 0):
        raise ValueError(f"f_k must be a positive integer, got {f_k}")
    if not (0 < p_hat <= 1):
        raise ValueError(f"p_hat must be in (0, 1], got {p_hat}")
    
    # Special case: when p_hat = 1, formula simplifies to 1/f_k
    if p_hat == 1.0:
        return 1.0 / f_k

    if f_k > 40:
        denominator = f_k - (1.0 - p_hat)
        if denominator <= 0:
            return 1.0
        r = p_hat / denominator
        return min(r, 1.0)

    q = 1 - p_hat
    r = (p_hat ** f_k) / f_k * hyp2f1(f_k, f_k, f_k + 1, q)

    # Numerically may be slightly greater than 1, clip if necessary
    return min(r, 1.0)


def find_rows_for_key(rows: list[dict], columns: list[str], key_values: tuple | list | dict) -> tuple[int, list[int], list[dict]]:
    """Return how many rows match the given key values, the row indices, and the matching rows.

    Parameters:
        rows: list of row dictionaries
        columns: list of columns that form the key
        key_values: target key values, either a tuple/list of values matching columns order,
            or a dict mapping column -> value

    Returns:
        (count, indices, matches)
    """
    if not rows:
        return 0, [], []

    header = list(rows[0].keys())
    missing = [col for col in columns if col not in header]
    if missing:
        raise ValueError(f"Missing columns in rows: {missing}")

    if isinstance(key_values, dict):
        target = tuple(key_values[col] for col in columns)
    else:
        target = tuple(key_values)
        if len(target) != len(columns):
            raise ValueError("key_values length must match columns length")

    indices = []
    matches = []
    for idx, row in enumerate(rows):
        if tuple(row.get(col) for col in columns) == target:
            indices.append(idx)
            matches.append(row)

    return len(matches), indices, matches


def calculate_p_hat(f_k, weights_k):
    """
    Calculate p_hat = f_k / sum(weights_k)

    """
    if f_k <= 0:
        raise ValueError(f"f_k must be positive, got {f_k}")
    
    total_weight = np.sum(weights_k)
    if total_weight <= 0:
        raise ValueError("sum of weights_k must be positive")
    
    p_hat = f_k / total_weight
    
    # Clip p_hat to the interval (0, 1]
    if p_hat > 1.0:
        p_hat = 1.0
    if p_hat <= 0:
        p_hat = 1e-10  # A very small positive value
    
    return p_hat


def load_csv(path: Path) -> list[dict]:
    for encoding in ("utf-8", "cp936"):
        try:
            with path.open(newline="", encoding=encoding) as f:
                reader = csv.DictReader(f)
                return [row for row in reader]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to read CSV file: {path}")


def parse_key_values(raw: str) -> tuple[str, ...]:
    values = [part.strip() for part in raw.split(",") if part.strip()]
    return tuple(values)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find key rows in a CSV and compute BF risk.")
    parser.add_argument("--csv", dest="csv_path", required=True, help="Path to CSV file")
    parser.add_argument(
        "--columns",
        required=True,
        help="Comma-separated list of key columns in order",
    )
    parser.add_argument(
        "--key",
        required=True,
        help="Comma-separated list of values for the key columns in the same order",
    )
    parser.add_argument(
        "--weight-column",
        default="weights_k",
        help="Name of the weight column to use for p_hat calculation",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows = load_csv(csv_path)
    columns = [col.strip() for col in args.columns.split(",") if col.strip()]
    target_key = parse_key_values(args.key)

    if len(target_key) != len(columns):
        raise ValueError("The number of key values must match the number of columns")

    count, indices, matches = find_rows_for_key(rows, columns, target_key)
    print(f"Matched rows: {count}")
    print(f"Row indices: {indices}")

    if count == 0:
        return

    if args.weight_column not in matches[0]:
        raise ValueError(f"Weight column '{args.weight_column}' not found in CSV")

    weights_k = []
    for row in matches:
        weight_value = row[args.weight_column]
        try:
            weights_k.append(float(weight_value))
        except ValueError as exc:
            raise ValueError(f"Invalid weight value '{weight_value}' in column '{args.weight_column}'") from exc

    p_hat = calculate_p_hat(count, weights_k)
    risk = bf_risk(count, p_hat)

    print(f"f_k = {count}")
    print(f"p_hat = {p_hat}")
    print(f"bf_risk = {risk}")


if __name__ == "__main__":
    main()


