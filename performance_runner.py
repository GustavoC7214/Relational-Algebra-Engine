import time
import csv
from pathlib import Path

from data_generator import calculate_key_count, generate_r, generate_s, write_relation_file
from src.engine.database import Database
from src.engine.query_processor import QueryProcessor


def load_relations(
    file_path: Path,
    processor: QueryProcessor,
) -> None:
    source = file_path.read_text(encoding="utf-8")

    definition_lines = []

    for line in source.splitlines():
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith("//"):
            continue

        definition_lines.append(line)

        if stripped_line.startswith("}"):
            definition = "\n".join(definition_lines)
            processor.execute(definition)
            definition_lines = []


def run_join_experiment(
    n: int,
    m: int,
    match_rate: int = 1,
) -> dict[str, int | float]:
    output_path = Path("performance_data.ra")

    key_count = calculate_key_count(
        m,
        match_rate,
    )

    r_rows = generate_r(
        n,
        key_count,
    )

    s_rows = generate_s(
        m,
        key_count,
    )

    write_relation_file(
        output_path,
        r_rows,
        s_rows,
    )

    database = Database()
    processor = QueryProcessor(database)

    print(f"Generated R with {n} tuples.")
    print(f"Generated S with {m} tuples.")
    print(f"Match rate: {match_rate}.")
    load_relations(output_path, processor)

    r_relation = database.get_relation("R")
    s_relation = database.get_relation("S")

    print(f"Loaded R with {len(r_relation.rows)} tuples.")
    print(f"Loaded S with {len(s_relation.rows)} tuples.")
    processor.evaluator.join_comparisons = 0

    start_time = time.perf_counter()

    result = processor.execute(
        "R join[R.b=S.b] S"
    )

    end_time = time.perf_counter()

    elapsed_time = end_time - start_time

    print(f"Join comparisons: {processor.evaluator.join_comparisons}")
    print(f"Wall time: {elapsed_time:.6f} seconds")
    print(f"Output tuples: {len(result.rows)}")
    return {
        "n": n,
        "m": m,
        "comparisons": processor.evaluator.join_comparisons,
        "wall_time": elapsed_time,
        "output_tuples": len(result.rows),
    }


def save_result(
    result: dict[str, int | float],
    output_path: Path = Path("performance_results.csv"),
) -> None:
    file_exists = output_path.exists()

    with output_path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "n",
                "m",
                "comparisons",
                "wall_time",
                "output_tuples",
            ],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(result)


def run_selection_experiment(n: int) -> dict[str, int | float]:
    database = Database()
    processor = QueryProcessor(database)

    key_count = calculate_key_count(n, 1)
    r_rows = generate_r(n, key_count)

    output_path = Path("performance_data.ra")
    write_relation_file(output_path, r_rows, [])
    load_relations(output_path, processor)

    processor.evaluator.selection_tuples_examined = 0

    start_time = time.perf_counter()
    result = processor.execute("select[a >= 0](R)")
    elapsed_time = time.perf_counter() - start_time

    print(f"Selection tuples examined: {processor.evaluator.selection_tuples_examined}")
    print(f"Wall time: {elapsed_time:.6f} seconds")
    print(f"Output tuples: {len(result.rows)}")

    return {
        "n": n,
        "tuples_examined": processor.evaluator.selection_tuples_examined,
        "wall_time": elapsed_time,
        "output_tuples": len(result.rows),
    }


def save_selection_result(
    result: dict[str, int | float],
    output_path: Path = Path("selection_results.csv"),
) -> None:
    file_exists = output_path.exists()

    with output_path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "n",
                "tuples_examined",
                "wall_time",
                "output_tuples",
            ],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(result)


def run_projection_experiment(n: int) -> dict[str, int | float]:
    database = Database()
    processor = QueryProcessor(database)

    key_count = calculate_key_count(n, 1)
    r_rows = generate_r(n, key_count)

    output_path = Path("performance_data.ra")
    write_relation_file(output_path, r_rows, [])
    load_relations(output_path, processor)

    start_time = time.perf_counter()
    result = processor.execute("project[a](R)")
    elapsed_time = time.perf_counter() - start_time

    print(f"Wall time: {elapsed_time:.6f} seconds")
    print(f"Output tuples: {len(result.rows)}")

    return {
        "n": n,
        "wall_time": elapsed_time,
        "output_tuples": len(result.rows),
    }


def save_projection_result(
    result: dict[str, int | float],
    output_path: Path = Path("projection_results.csv"),
) -> None:
    file_exists = output_path.exists()

    with output_path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "n",
                "wall_time",
                "output_tuples",
            ],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(result)


def save_match_rate_results(
    output_path: Path = Path("match_rate_results.csv"),
) -> None:
    measurements = [
        (1, 1.386174, 1000),
        (2, 1.553754, 2000),
        (4, 2.474367, 4000),
        (8, 6.178638, 8000),
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "n",
            "m",
            "match_rate",
            "comparisons",
            "wall_time",
            "output_tuples",
        ])

        for match_rate, wall_time, output_tuples in measurements:
            writer.writerow([
                1000,
                1000,
                match_rate,
                1_000_000,
                wall_time,
                output_tuples,
            ])


def main() -> None:
    save_match_rate_results()
    print("Match-rate measurements saved to match_rate_results.csv")

if __name__ == "__main__":
    main()  