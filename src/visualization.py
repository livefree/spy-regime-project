from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#e76f51", "#2a9d8f", "#264653", "#f4a261", "#457b9d", "#8ab17d"]


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_regime_rows(input_path: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with open(resolve_path(input_path), "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def make_color_map(labels: list[str]) -> dict[str, str]:
    uniq = sorted(set(labels))
    return {label: COLORS[i % len(COLORS)] for i, label in enumerate(uniq)}


def plot_overlay(
    dates: list[datetime],
    values: list[float],
    labels: list[str],
    y_label: str,
    title: str,
    output_path: str,
) -> None:
    color_map = make_color_map(labels)
    point_colors = [color_map[label] for label in labels]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, values, color="#9aa0a6", linewidth=1.2, alpha=0.6)
    ax.scatter(dates, values, c=point_colors, s=8, alpha=0.85)

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", label=f"regime {label}",
                   markerfacecolor=color, markersize=7)
        for label, color in color_map.items()
    ]
    ax.legend(handles=handles, loc="best")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(y_label)
    fig.autofmt_xdate()
    fig.tight_layout()

    out = resolve_path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)


def run_visualization(
    input_path: str = "data/spy_2008_2024_regimes.csv",
    label_column: str = "cluster_k3",
    close_plot_path: str = "experiments/close_regime_overlay.png",
    vol_plot_path: str = "experiments/vol30_regime_overlay.png",
) -> tuple[str, str]:
    rows = load_regime_rows(input_path)
    if not rows:
        raise ValueError("No rows found in regime input file.")
    if label_column not in rows[0]:
        raise ValueError(f"Column '{label_column}' not found in input.")

    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
    close_vals = [float(row["close"]) for row in rows]
    vol30_vals = [float(row["vol30"]) for row in rows]
    labels = [row[label_column] for row in rows]

    plot_overlay(
        dates=dates,
        values=close_vals,
        labels=labels,
        y_label="Close Price",
        title=f"SPY Close Price with Regime Overlay ({label_column})",
        output_path=close_plot_path,
    )
    plot_overlay(
        dates=dates,
        values=vol30_vals,
        labels=labels,
        y_label="30D Rolling Volatility",
        title=f"30D Rolling Volatility with Regime Overlay ({label_column})",
        output_path=vol_plot_path,
    )
    return close_plot_path, vol_plot_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/spy_2008_2024_regimes.csv")
    parser.add_argument("--label-column", default="cluster_k3")
    parser.add_argument("--close-output", default="experiments/close_regime_overlay.png")
    parser.add_argument("--vol-output", default="experiments/vol30_regime_overlay.png")
    args = parser.parse_args()

    close_out, vol_out = run_visualization(
        input_path=args.input,
        label_column=args.label_column,
        close_plot_path=args.close_output,
        vol_plot_path=args.vol_output,
    )
    print(f"saved {close_out}")
    print(f"saved {vol_out}")


if __name__ == "__main__":
    main()
