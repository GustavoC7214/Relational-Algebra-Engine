import csv
import math
from pathlib import Path


def main() -> None:
    csv_path = Path("performance_results.csv")

    with csv_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    sizes = [int(row["n"]) for row in rows]
    times = [float(row["wall_time"]) for row in rows]

    log_sizes = [math.log(size) for size in sizes]
    log_times = [math.log(seconds) for seconds in times]

    mean_x = sum(log_sizes) / len(log_sizes)
    mean_y = sum(log_times) / len(log_times)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(log_sizes, log_times)
    )
    denominator = sum((x - mean_x) ** 2 for x in log_sizes)

    slope = numerator / denominator

    # Extrapolate from the largest measured input using the measured slope.
    largest_n = sizes[-1]
    largest_time = times[-1]
    target_n = 1_000_000

    predicted_seconds = largest_time * (target_n / largest_n) ** slope

    print(f"Measured log-log slope: {slope:.4f}")
    print(f"Largest measured size: n = m = {largest_n:,}")
    print(f"Largest measured wall time: {largest_time:.3f} seconds")
    print(f"Predicted time for n = m = {target_n:,}:")
    print(f"  {predicted_seconds:,.0f} seconds")
    print(f"  {predicted_seconds / 3600:,.2f} hours")
    print(f"  {predicted_seconds / 86400:,.2f} days")


if __name__ == "__main__":
    main()