from __future__ import annotations

import argparse
import csv
import math
from datetime import date
from pathlib import Path


def parse_yyyy_m_d(value: str) -> date:
    y, m, d = value.split("-")
    return date(int(y), int(m), int(d))


def build_dataset(
    input_path: str = "data/spy.csv",
    output_path: str = "data/spy_2008_2024_returns.csv",
    start_date: str = "2008-01-01",
    end_date: str = "2024-12-31",
) -> list[dict[str, str]]:
    start = parse_yyyy_m_d(start_date)
    end = parse_yyyy_m_d(end_date)

    rows: list[tuple[date, float]] = []
    with open(input_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = parse_yyyy_m_d(row["Date"])
            if start <= d <= end:
                rows.append((d, float(row["Close"])))

    rows.sort(key=lambda x: x[0])

    result: list[dict[str, str]] = []
    prev_close: float | None = None
    for d, close in rows:
        if prev_close is not None:
            log_ret = math.log(close / prev_close)
            result.append(
                {"date": d.isoformat(), "close": f"{close}", "return": f"{log_ret}"}
            )
        prev_close = close

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "close", "return"])
        writer.writeheader()
        writer.writerows(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/spy.csv")
    parser.add_argument("--output", default="data/spy_2008_2024_returns.csv")
    parser.add_argument("--start-date", default="2008-01-01")
    parser.add_argument("--end-date", default="2024-12-31")
    args = parser.parse_args()

    result = build_dataset(
        input_path=args.input,
        output_path=args.output,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    print(f"saved {len(result)} rows to {args.output}")


if __name__ == "__main__":
    main()
