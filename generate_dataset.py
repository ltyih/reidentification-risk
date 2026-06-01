"""
Synthetic dataset generator for re-identification research.

Usage:
    python3 generate_dataset.py [--rows N] [--seed S] [--output FILE]

Tune the CONFIG section below to control variable counts, ranges, and noise.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from dataclasses import dataclass, field
from typing import Any

import numpy as np


# =============================================================================
# CONFIG
# =============================================================================

N_CATEGORICAL   = 20    # variables with 3–8 random categories
N_LIKERT        = 50    # 5-point Likert scale items
N_CONTINUOUS    = 30    # continuous numeric variables

# Noise = fraction of rows that receive a corrupted/outlier value per variable.
# Set to 0.0 to disable noise on a group.
NOISE_DEMO       = 0.02
NOISE_CATEGORICAL = 0.02
NOISE_LIKERT     = 0.01
NOISE_CONTINUOUS  = 0.02

# Seed used when building the variable definitions themselves (not the data seed).
SCHEMA_SEED = 0


# =============================================================================
# VARIABLE DEFINITIONS
# =============================================================================

@dataclass
class VarConfig:
    name: str
    kind: str           # "categorical" | "continuous" | "boolean" | "id"
    categories: list[str] = field(default_factory=list)
    weights: list[float] | None = None
    low: float = 0.0
    high: float = 100.0
    decimals: int = 2
    distribution: str = "uniform"   # "uniform" | "normal" | "skewed"
    mean: float | None = None
    std: float | None = None
    noise: float = 0.0
    id_prefix: str = "ID"


# --- Demographics (explicit) -------------------------------------------------

DEMOGRAPHICS: list[VarConfig] = [
    VarConfig("record_id", "id", id_prefix="P"),
    VarConfig(
        "age", "continuous",
        low=18, high=90, decimals=0,
        distribution="normal", mean=45, std=15,
        noise=NOISE_DEMO,
    ),
    VarConfig(
        "sex", "categorical",
        categories=["Male", "Female", "Non-binary", "Prefer not to say"],
        weights=[0.48, 0.48, 0.02, 0.02],
        noise=NOISE_DEMO,
    ),
    VarConfig(
        "zip_code", "categorical",
        categories=["10001", "10002", "10003", "10004", "10005",
                    "90210", "60601", "77001", "30301", "98101"],
        noise=NOISE_DEMO,
    ),
    VarConfig(
        "income_bracket", "categorical",
        categories=["<$25k", "$25k–$50k", "$50k–$75k", "$75k–$100k", ">$100k"],
        weights=[0.15, 0.25, 0.30, 0.20, 0.10],
        noise=NOISE_DEMO,
    ),
    VarConfig(
        "education_level", "categorical",
        categories=["No diploma", "High school", "Some college",
                    "Bachelor's", "Graduate degree"],
        weights=[0.05, 0.28, 0.22, 0.30, 0.15],
        noise=NOISE_DEMO,
    ),
    VarConfig("has_chronic_condition", "boolean", noise=NOISE_DEMO),
    VarConfig(
        "bmi", "continuous",
        low=15.0, high=55.0, decimals=1,
        distribution="normal", mean=27.5, std=5.5,
        noise=NOISE_DEMO,
    ),
    VarConfig(
        "num_doctor_visits", "continuous",
        low=0, high=30, decimals=0,
        distribution="skewed",
        noise=NOISE_DEMO,
    ),
    VarConfig(
        "smoker", "categorical",
        categories=["Never", "Former", "Current"],
        weights=[0.60, 0.25, 0.15],
        noise=NOISE_DEMO,
    ),
]


# --- Programmatically-generated variable groups -----------------------------

def _make_categorical_vars(n: int, seed: int, noise: float) -> list[VarConfig]:
    """Generate n categorical variables, each with 3–8 randomly-named categories."""
    rng = random.Random(seed)

    generic_pools = [
        ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta"],
        ["Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Brown", "Pink"],
        ["North", "South", "East", "West", "Central", "Upper", "Lower", "Outer"],
        ["Type A", "Type B", "Type C", "Type D", "Type E", "Type F", "Type G", "Type H"],
        ["Low", "Medium", "High", "Very High", "Extreme", "Moderate", "Minimal", "Trace"],
        ["Urban", "Suburban", "Rural", "Remote", "Coastal", "Inland", "Border", "Metro"],
        ["Spring", "Summer", "Autumn", "Winter", "Dry", "Wet", "Monsoon", "Temperate"],
        ["Group 1", "Group 2", "Group 3", "Group 4",
         "Group 5", "Group 6", "Group 7", "Group 8"],
    ]

    configs = []
    for i in range(1, n + 1):
        pool = rng.choice(generic_pools)
        k = rng.randint(3, len(pool))
        categories = rng.sample(pool, k)
        # Random skew: sometimes uniform, sometimes weighted toward first few
        if rng.random() < 0.5:
            raw_w = [rng.uniform(0.5, 3.0) for _ in categories]
            total = sum(raw_w)
            weights = [w / total for w in raw_w]
        else:
            weights = None
        configs.append(VarConfig(
            name=f"cat_{i:02d}",
            kind="categorical",
            categories=categories,
            weights=weights,
            noise=noise,
        ))
    return configs


def _make_likert_vars(n: int, noise: float) -> list[VarConfig]:
    """Generate n 5-point Likert scale variables."""
    scale = [
        "Strongly disagree",
        "Disagree",
        "Neutral",
        "Agree",
        "Strongly agree",
    ]
    return [
        VarConfig(
            name=f"likert_{i:02d}",
            kind="categorical",
            categories=scale,
            noise=noise,
        )
        for i in range(1, n + 1)
    ]


def _make_continuous_vars(n: int, seed: int, noise: float) -> list[VarConfig]:
    """Generate n continuous variables with varied ranges and distributions."""
    rng = random.Random(seed)

    templates = [
        # (low, high, decimals, distribution)
        (0.0,   1.0,   3, "uniform"),
        (0.0,   100.0, 1, "uniform"),
        (0.0,   1000.0,0, "skewed"),
        (18.0,  80.0,  1, "normal"),
        (-5.0,  5.0,   3, "normal"),
        (0.0,   10.0,  2, "normal"),
        (1.0,   500.0, 0, "skewed"),
        (0.0,   50.0,  1, "uniform"),
    ]

    configs = []
    for i in range(1, n + 1):
        low, high, decimals, dist = rng.choice(templates)
        mu = (low + high) / 2
        sigma = (high - low) / 6
        configs.append(VarConfig(
            name=f"cont_{i:02d}",
            kind="continuous",
            low=low, high=high,
            decimals=decimals,
            distribution=dist,
            mean=mu,
            std=sigma,
            noise=noise,
        ))
    return configs


# Build the full schema once at import time
VARIABLE_CONFIG: list[VarConfig] = (
    DEMOGRAPHICS
    + _make_categorical_vars(N_CATEGORICAL, seed=SCHEMA_SEED,     noise=NOISE_CATEGORICAL)
    + _make_likert_vars(N_LIKERT,                                  noise=NOISE_LIKERT)
    + _make_continuous_vars(N_CONTINUOUS, seed=SCHEMA_SEED + 1,   noise=NOISE_CONTINUOUS)
)


# =============================================================================
# VALUE GENERATION
# =============================================================================

def _corrupt(value: Any, cfg: VarConfig,
             rng: random.Random, np_rng: np.random.Generator) -> Any:
    if cfg.kind == "categorical":
        return rng.choice(cfg.categories)
    if cfg.kind == "continuous":
        span = cfg.high - cfg.low
        direction = rng.choice([-1, 1])
        outlier = cfg.low + direction * span * np_rng.uniform(0.05, 0.30)
        return round(float(outlier), cfg.decimals)
    if cfg.kind == "boolean":
        return not value
    return value


def _generate_value(cfg: VarConfig, row_index: int,
                    rng: random.Random, np_rng: np.random.Generator) -> Any:
    if cfg.kind == "id":
        return f"{cfg.id_prefix}{row_index + 1:06d}"

    if cfg.kind == "boolean":
        raw = rng.random() < 0.5

    elif cfg.kind == "categorical":
        raw = rng.choices(cfg.categories, weights=cfg.weights, k=1)[0]

    elif cfg.kind == "continuous":
        if cfg.distribution == "normal":
            mu = cfg.mean if cfg.mean is not None else (cfg.low + cfg.high) / 2
            sigma = cfg.std if cfg.std is not None else (cfg.high - cfg.low) / 6
            raw = float(np.clip(np_rng.normal(mu, sigma), cfg.low, cfg.high))
        elif cfg.distribution == "skewed":
            raw = float(np.clip(np_rng.lognormal(1.5, 0.8), cfg.low, cfg.high))
        else:
            raw = float(np_rng.uniform(cfg.low, cfg.high))
        raw = round(raw, cfg.decimals)
        if cfg.decimals == 0:
            raw = int(raw)

    else:
        raw = None

    if cfg.noise > 0 and rng.random() < cfg.noise:
        raw = _corrupt(raw, cfg, rng, np_rng)

    return raw


# =============================================================================
# DATASET ASSEMBLY
# =============================================================================

def generate_dataset(n_rows: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    return [
        {cfg.name: _generate_value(cfg, i, rng, np_rng) for cfg in VARIABLE_CONFIG}
        for i in range(n_rows)
    ]


# =============================================================================
# OUTPUT
# =============================================================================

def _print_table(rows: list[dict]) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    col_w = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
    sep = "+-" + "-+-".join("-" * col_w[h] for h in headers) + "-+"
    fmt = lambda r: "| " + " | ".join(str(r[h]).ljust(col_w[h]) for h in headers) + " |"
    print(sep)
    print(fmt({h: h for h in headers}))
    print(sep)
    for row in rows:
        print(fmt(row))
    print(sep)


def _write_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows → {path}", file=sys.stderr)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic dataset.")
    parser.add_argument("--rows",   type=int, default=20,   help="Number of individuals")
    parser.add_argument("--seed",   type=int, default=42,   help="Random seed")
    parser.add_argument("--output", type=str, default=None, help="CSV output path")
    args = parser.parse_args()

    total_vars = len(VARIABLE_CONFIG)
    print(f"Schema: {total_vars} variables — generating {args.rows} rows …", file=sys.stderr)

    dataset = generate_dataset(args.rows, args.seed)

    if args.output:
        _write_csv(dataset, args.output)
    else:
        _print_table(dataset)


if __name__ == "__main__":
    main()
