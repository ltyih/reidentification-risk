import argparse
import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))



PROVINCE_ABBREVIATIONS = {
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia",
    "NT": "Northwest Territories",
    "NU": "Nunavut",
    "ON": "Ontario",
    "PE": "Prince Edward Island",
    "QC": "Quebec",
    "SK": "Saskatchewan",
    "YT": "Yukon",
}

NORMALIZED_ABBREVIATIONS = {key.lower(): value for key, value in PROVINCE_ABBREVIATIONS.items()}

POSTAL_PREFIX_TO_ABBREV = {
    "A": "NL",
    "B": "NS",
    "C": "PE",
    "E": "NB",
    "G": "QC",
    "H": "QC",
    "J": "QC",
    "K": "ON",
    "L": "ON",
    "M": "ON",
    "N": "ON",
    "P": "ON",
    "R": "MB",
    "S": "SK",
    "T": "AB",
    "V": "BC",
    "X": "NT",
    "Y": "YT",
}


def load_csv(path: Path) -> list[dict]:
    for encoding in ("utf-8", "cp936"):
        try:
            with path.open(newline="", encoding=encoding) as f:
                reader = csv.DictReader(f)
                return [row for row in reader]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to read CSV file: {path}")


def write_csv(path: Path, rows: list[dict], fieldnames: Iterable[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_gender(value: object) -> str:
    text = normalize_text(value).lower()
    if text in {"m", "male", "M", "Male"}:
        return "male"
    if text in {"f", "female", "F", "Female"}:
        return "female"
    return text


def postal_code_to_province_abbrev(value: object) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    code = text.replace(" ", "").upper()
    if not code:
        return ""
    prefix = code[0]
    return POSTAL_PREFIX_TO_ABBREV.get(prefix, "")


def normalize_region(value: object, region_map: dict[str, str]) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    lower = text.lower()
    if lower in region_map:
        return region_map[lower]
    if lower in (name.lower() for name in region_map.values()):
        return next(name for name in region_map.values() if name.lower() == lower)

    # If the value looks like a postal code, infer the province abbreviation
    province_abbrev = postal_code_to_province_abbrev(text)
    if province_abbrev:
        abbrev_lower = province_abbrev.lower()
        if abbrev_lower in region_map:
            return region_map[abbrev_lower]

    return text


def parse_age_ranges(age_labels: Iterable[str]) -> list[tuple[int, int, str]]:
    ranges = []
    for label in sorted({normalize_text(label) for label in age_labels}):
        if not label:
            continue
        if "+" in label:
            low_text = label.replace("+", "").strip()
            low = int(low_text)
            ranges.append((low, 200, label))
            continue

        if "to" in label:
            parts = [part.strip() for part in label.split("to", 1)]
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                ranges.append((int(parts[0]), int(parts[1]), label))
                continue

        raise ValueError(f"Unable to parse age range label: {label}")
    return ranges


def assign_age_group(age_value: object, age_ranges: list[tuple[int, int, str]]) -> str:
    raw = normalize_text(age_value)
    if raw == "":
        raise ValueError("Missing age value")

    if raw.isdigit():
        age = int(raw)
    else:
        try:
            age = int(float(raw))
        except ValueError:
            for _, _, label in age_ranges:
                if normalize_text(raw).lower() == normalize_text(label).lower():
                    return label
            raise ValueError(f"Unable to convert age value to numeric age: {age_value}")

    for low, high, label in age_ranges:
        if low <= age <= high:
            return label

    raise ValueError(f"Age {age} does not fall into any known age group")


def build_population_index(pop_rows: list[dict], region_col: str, age_col: str, gender_col: str) -> tuple[dict[tuple[str, str, str], float], list[tuple[int, int, str]]]:
    age_ranges = parse_age_ranges(row[age_col] for row in pop_rows)
    populations = {}

    for row in pop_rows:
        region = normalize_region(row[region_col], NORMALIZED_ABBREVIATIONS)
        gender = normalize_gender(row[gender_col])
        age_label = normalize_text(row[age_col])
        population = row.get("population")
        if population is None or normalize_text(population) == "":
            raise ValueError(f"Missing population for row: {row}")
        population_value = float(population)
        key = (region, age_label, gender)
        if key in populations:
            raise ValueError(f"Duplicate population key found: {key}")
        populations[key] = population_value

    return populations, age_ranges



def generate_weights(
    data_path: Path,
    pop_path: Path,
    data_region_col: str,
    data_age_col: str,
    data_gender_col: str,
    pop_region_col: str = "geography",
    pop_age_col: str = "age",
    pop_gender_col: str = "gender",
    output_path: Path | None = None,
) -> Path:
    data_rows = load_csv(data_path)
    pop_rows = load_csv(pop_path)

    if not data_rows:
        raise ValueError(f"Data file is empty: {data_path}")
    if not pop_rows:
        raise ValueError(f"Population file is empty: {pop_path}")

    populations, age_ranges = build_population_index(pop_rows, pop_region_col, pop_age_col, pop_gender_col)

    for row in data_rows:
        row["_region_norm"] = normalize_region(row.get(data_region_col), NORMALIZED_ABBREVIATIONS)
        row["_gender_norm"] = normalize_gender(row.get(data_gender_col))
        row["_age_group"] = assign_age_group(row.get(data_age_col), age_ranges)

        if not row["_region_norm"]:
            raise ValueError(f"Empty normalized region for row: {row}")
        if not row["_gender_norm"]:
            raise ValueError(f"Empty normalized gender for row: {row}")

    sample_counts = Counter(
        (row["_region_norm"], row["_age_group"], row["_gender_norm"]) for row in data_rows
    )

    lookup_columns = ["_region_norm", "_age_group", "_gender_norm"]
    for row in data_rows:
        combo = (row["_region_norm"], row["_age_group"], row["_gender_norm"])
        if combo not in populations:
            raise ValueError(
                f"No matching population key for row group {combo}. "
                f"Check region/age/gender mapping and whether pop.csv has the same groups."
            )

        sample_frequency = sample_counts[combo]
        if sample_frequency <= 0:
            raise ValueError(f"Sample frequency for group {combo} is not positive")
        
        print(f"combo: {combo}, frequency: {sample_frequency}, population: {populations[combo]}")
      
        population = populations[combo]
        weight = population / sample_frequency
        row["weight"] = weight

    output_path = output_path or data_path.with_name(f"{data_path.stem}_weighted{data_path.suffix}")
    output_fieldnames = [name for name in data_rows[0].keys() if not name.startswith("_")]
    # Clean up temporary fields before writing
    for row in data_rows:
        for key in list(row.keys()):
            if key.startswith("_"):
                del row[key]
    write_csv(output_path, data_rows, output_fieldnames)
    return output_path


def resolve_input_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.exists():
        return path
    fallback = ROOT / path_str
    if fallback.exists():
        return fallback
    if path.parent == Path('.') and (ROOT / 'data' / path.name).exists():
        return ROOT / 'data' / path.name
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample weights from a data CSV and a population CSV.")
    parser.add_argument("--data", required=True, help="Input data CSV path")
    parser.add_argument("--pop", required=True, help="Population CSV path")
    parser.add_argument(
        "--region-col",
        default="region",
        help="Region column name in data CSV. Can be a province name, abbreviation, or postal code/address.",
    )
    parser.add_argument("--age-col", default="age", help="Age column name in data CSV")
    parser.add_argument("--gender-col", default="sex", help="Gender column name in data CSV")
    parser.add_argument(
        "--output",
        help="Output CSV path. Defaults to <data>_weighted.csv",
    )
    args = parser.parse_args()

    data_path = resolve_input_path(args.data)
    pop_path = resolve_input_path(args.pop)
    output_path = Path(args.output) if args.output else None
    if output_path and not output_path.is_absolute():
        output_path = ROOT / output_path

    if not data_path.exists():
        raise FileNotFoundError(f"Data CSV not found: {data_path}")
    if not pop_path.exists():
        raise FileNotFoundError(f"Population CSV not found: {pop_path}")

    out = generate_weights(
        data_path=data_path,
        pop_path=pop_path,
        data_region_col=args.region_col,
        data_age_col=args.age_col,
        data_gender_col=args.gender_col,
        output_path=output_path,
    )
    print(f"Weighted CSV created: {out}")


if __name__ == "__main__":
    main()
