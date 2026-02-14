from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else PROJECT_ROOT / path


def rolling_mean(values: list[float]) -> float:
    return sum(values) / len(values)


def rolling_vol(values: list[float]) -> float:
    # Use population std for a stable, simple volatility proxy.
    return statistics.pstdev(values)


def build_features(
    input_path: str = "data/spy_2008_2024_returns.csv",
    output_path: str = "data/spy_2008_2024_features.csv",
) -> list[dict[str, str]]:
    in_path = resolve_path(input_path)
    out_path = resolve_path(output_path)

    rows: list[dict[str, str]] = []
    with open(in_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "date": row["date"],
                    "close": row["close"],
                    "return": row["return"],
                }
            )

    returns = [float(r["return"]) for r in rows]
    result: list[dict[str, str]] = []

    for i, row in enumerate(rows):
        if i < 29 or i < 3:
            continue

        win10 = returns[i - 9 : i + 1]
        win30 = returns[i - 29 : i + 1]

        record = {
            "date": row["date"],
            "close": row["close"],
            "return": row["return"],
            "vol10": f"{rolling_vol(win10)}",
            "vol30": f"{rolling_vol(win30)}",
            "mean10": f"{rolling_mean(win10)}",
            "mean30": f"{rolling_mean(win30)}",
            "r_lag1": f"{returns[i - 1]}",
            "r_lag2": f"{returns[i - 2]}",
            "r_lag3": f"{returns[i - 3]}",
        }
        result.append(record)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "close",
                "return",
                "vol10",
                "vol30",
                "mean10",
                "mean30",
                "r_lag1",
                "r_lag2",
                "r_lag3",
            ],
        )
        writer.writeheader()
        writer.writerows(result)

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/spy_2008_2024_returns.csv")
    parser.add_argument("--output", default="data/spy_2008_2024_features.csv")
    args = parser.parse_args()

    features = build_features(input_path=args.input, output_path=args.output)
    print(f"saved {len(features)} rows to {args.output}")


if __name__ == "__main__":
    main()
