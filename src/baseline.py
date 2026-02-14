from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_COLUMNS = ["vol10", "vol30", "mean10", "mean30", "r_lag1", "r_lag2", "r_lag3"]


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else PROJECT_ROOT / path


def euclidean_sq(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def mean_vector(points: list[list[float]]) -> list[float]:
    dims = len(points[0])
    return [sum(p[d] for p in points) / len(points) for d in range(dims)]


def standardize_matrix(matrix: list[list[float]]) -> list[list[float]]:
    rows = len(matrix)
    cols = len(matrix[0])
    means = [sum(matrix[r][c] for r in range(rows)) / rows for c in range(cols)]
    stds: list[float] = []
    for c in range(cols):
        var = sum((matrix[r][c] - means[c]) ** 2 for r in range(rows)) / rows
        std = math.sqrt(var)
        stds.append(std if std > 0 else 1.0)

    return [[(matrix[r][c] - means[c]) / stds[c] for c in range(cols)] for r in range(rows)]


def init_centroids(data: list[list[float]], k: int) -> list[list[float]]:
    n = len(data)
    # Deterministic spread across the series for reproducibility.
    return [data[(i * n) // k][:] for i in range(k)]


def kmeans(data: list[list[float]], k: int, max_iter: int = 200) -> list[int]:
    centroids = init_centroids(data, k)
    labels = [-1] * len(data)

    for _ in range(max_iter):
        changed = False
        for i, point in enumerate(data):
            label = min(range(k), key=lambda j: euclidean_sq(point, centroids[j]))
            if labels[i] != label:
                labels[i] = label
                changed = True

        if not changed:
            break

        clusters: list[list[list[float]]] = [[] for _ in range(k)]
        for i, label in enumerate(labels):
            clusters[label].append(data[i])

        for j in range(k):
            if clusters[j]:
                centroids[j] = mean_vector(clusters[j])

    return labels


def run_baseline(
    input_path: str = "data/spy_2008_2024_features.csv",
    output_path: str = "data/spy_2008_2024_regimes.csv",
) -> list[dict[str, str]]:
    in_path = resolve_path(input_path)
    out_path = resolve_path(output_path)

    rows: list[dict[str, str]] = []
    with open(in_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    matrix = [[float(row[col]) for col in FEATURE_COLUMNS] for row in rows]
    x = standardize_matrix(matrix)

    labels_k2 = kmeans(x, k=2)
    labels_k3 = kmeans(x, k=3)

    result: list[dict[str, str]] = []
    for i, row in enumerate(rows):
        out = dict(row)
        out["cluster_k2"] = str(labels_k2[i])
        out["cluster_k3"] = str(labels_k3[i])
        result.append(out)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) + ["cluster_k2", "cluster_k3"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/spy_2008_2024_features.csv")
    parser.add_argument("--output", default="data/spy_2008_2024_regimes.csv")
    args = parser.parse_args()

    rows = run_baseline(input_path=args.input, output_path=args.output)
    print(f"saved {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
