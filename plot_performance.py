import csv
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    with Path("performance_results.csv").open(
        newline="", encoding="utf-8"
    ) as file:
        rows = list(csv.DictReader(file))

    sizes = [int(row["n"]) for row in rows]
    times = [float(row["wall_time"]) for row in rows]

    plt.figure(figsize=(8, 5))
    plt.loglog(
        sizes,
        times,
        marker="o",
        label="Measured join wall time",
    )

    plt.xlabel("Input size (n = m)")
    plt.ylabel("Wall time (seconds)")
    plt.title("Nested-Loop Join Scaling")
    plt.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()

    output_path = Path("join_scaling.png")
    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()