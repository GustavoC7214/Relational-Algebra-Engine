# Relational Algebra Engine

A hand-written relational algebra query processor built in Python for COMP 3005 — Database Management Systems at Carleton University.

The engine tokenizes and parses a small relational algebra language, builds an abstract syntax tree (AST), and evaluates queries against relations loaded from a text file. It supports nested expressions, set operations, theta joins, Boolean conditions, parse-tree output, and source-position-aware error reporting.

The tokenizer and recursive-descent parser are implemented manually without regular expressions, parser generators, `eval`, or `exec`.

## Requirements and Setup

Python 3 is required. The project was benchmarked using Python 3.14.6.

From the project root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install pytest to run the automated tests:

```bash
python -m pip install pytest
```

The query processor itself uses the Python standard library. Matplotlib is needed only if you want to regenerate the performance plot:

```bash
python -m pip install matplotlib
```

## Running Queries

The command-line entry point is `ra.py`. Run the following commands from the project root.

Load the example relations and execute a query:

```bash
python ra.py --file tests/relations.ra "project[Name, Age](select[Age>25](Member))"
```

Print a query's parse tree without evaluating it:

```bash
python ra.py --tree "project[Name](select[Age>25](Member))"
```

The `--tree` option does not require a relation file.

### Relation Definitions

Relations can be defined in a text file using the following format:

```text
Employees (EID, Name, Age, DID) = {
E1, John, 32, D1
E2, Alice, 28, D2
E3, Bob, 29, D1
}
```

Relation definitions support quoted and unquoted values, comments, and multiline input.

### Supported Operations

| Operation | Example |
|---|---|
| Selection | `select[Age>=30](Employees)` |
| Projection | `project[Name, Age](Employees)` |
| Rename | `rename[Staff](Employees)` |
| Sorting | `sort[Age desc](Employees)` |
| Union | `R union S` |
| Intersection | `R intersect S` |
| Difference | `R minus S` |
| Cartesian product | `R times S` |
| Theta join | `Employees join[Employees.DID=Departments.DID] Departments` |

Expressions can be nested. Conditions support `=`, `!=`, `<`, `<=`, `>`, `>=`, `not`, `and`, `or`, and parentheses.

For example:

```text
project[Name](select[Age>=30 and Name!='Bob'](Employees))
```

Relational and Boolean operator precedence, associativity, and the complete EBNF grammar are documented in [`docs/GRAMMAR.md`](docs/GRAMMAR.md).

## Errors

The command-line interface distinguishes lexical, syntax, name, schema, type, file, and usage errors.

The tokenizer records source positions so lexical errors can identify where an invalid character or unterminated string occurs.

## Running Tests

From the project root, run the complete automated test suite:

```bash
python -m pytest tests/ -q
```

The tests cover tokenization, parsing, AST tree printing, relations, database operations, query evaluation, query-processor integration, command-line behavior, and data generation.

## Performance Evaluation

The project includes a data generator and benchmark runner for join, selection, and projection experiments.

The completed benchmark results are saved in:

- `performance_results.csv` — join scaling measurements
- `selection_results.csv` — selection scaling measurements
- `projection_results.csv` — projection scaling measurements
- `match_rate_results.csv` — join measurements at different match rates

The performance analysis, measured results, extrapolation, and limitations are documented in [`docs/REPORT.md`](docs/REPORT.md). The join scaling plot is saved as [`join_scaling.png`](join_scaling.png).

The supporting scripts are:

- `data_generator.py` — generates benchmark relations
- `performance_runner.py` — runs performance experiments
- `analyze_performance.py` — calculates the join scaling slope and extrapolation
- `plot_performance.py` — generates the join scaling plot

**Note:** `performance_runner.py` currently runs whichever experiment is selected in its `main()` function. Running the full join-scaling experiment can take a long time; the completed measurements are already included in the CSV files.

## Project Structure

```text
Relational-Algebra-Engine/
├── docs/
│   ├── DESIGN_LOG.md
│   ├── GRAMMAR.md
│   └── REPORT.md
├── src/
│   ├── engine/
│   │   ├── database.py
│   │   ├── evaluator.py
│   │   ├── query_processor.py
│   │   └── relation.py
│   ├── lexer/
│   │   ├── token.py
│   │   └── tokenizer.py
│   └── parser/
│       ├── ast.py
│       ├── parser.py
│       └── tree_printer.py
├── tests/
│   ├── relations.ra
│   ├── test_cli.py
│   ├── test_data_generator.py
│   ├── test_database.py
│   ├── test_evaluator.py
│   ├── test_parser.py
│   ├── test_query_processor.py
│   ├── test_relation.py
│   ├── test_tokenizer.py
│   └── test_tree_printer.py
├── analyze_performance.py
├── data_generator.py
├── performance_runner.py
├── plot_performance.py
├── ra.py
├── join_scaling.png
├── performance_results.csv
├── selection_results.csv
├── projection_results.csv
├── match_rate_results.csv
└── README.md
```

## Development Documentation

[`docs/DESIGN_LOG.md`](docs/DESIGN_LOG.md) records the implementation decisions, testing, problems encountered, and AI assistance used during development.