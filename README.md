# Relational Algebra Engine

A hand-written relational algebra query processor built in Python.

The project implements a small relational algebra language from the ground up, including lexical analysis, parsing, relational expression representation, and eventually query execution. The language supports relation definitions, relational algebra operators, Boolean conditions, quoted and unquoted values, comments, and source-position-aware error reporting.

The project is being developed as part of COMP 3005 — Database Management Systems at Carleton University.

## Project Status

The project is currently under development.

### Completed

- EBNF grammar design
- Operator precedence and associativity rules
- Hand-written tokenizer
- Source position tracking
- Lexical error reporting
- Relation-definition tokenization
- Comment handling
- Quoted and bare string handling
- Automated tokenizer test suite

### Currently In Progress

- Abstract Syntax Tree (AST) design
- Recursive-descent parser

### Planned

- Relational algebra execution engine
- Semantic validation
- Relation storage and manipulation
- Query evaluation
- Parser and semantic test suites

---

## Supported Language

The language is designed to support relation definitions such as:

```text
Employees (EID, Name, Age, DID) = {
E1, John, 32, D1
E2, Alice, 28, D2
E3, Bob, 29, D1
}
```

### Unary Relational Operators

Selection:

```text
select[Age>=30](Employees)
```

Projection:

```text
project[Name, Age](Employees)
```

Rename:

```text
rename[Staff](Employees)
```

### Binary Relational Operators

Union:

```text
Employees union Managers
```

Intersection:

```text
R intersect S
```

Difference:

```text
R minus S
```

Cartesian product:

```text
R times S
```

Theta join:

```text
Employees join[Employees.DID=Departments.DID] Departments
```

### Boolean Conditions

Conditions support the following comparison and Boolean operators:

- `=`
- `!=`
- `<`
- `<=`
- `>`
- `>=`
- `not`
- `and`
- `or`
- Parentheses

For example:

```text
select[Age>=30 and Name!='Bob'](Employees)
```

Conditions use the following precedence, from highest to lowest:

1. Comparison operators
2. `not`
3. `and`
4. `or`

---

## Relational Operator Precedence

Relational expressions use the following precedence, from highest to lowest:

1. `select`, `project`, `rename`, and parenthesized expressions
2. `times` and `join`
3. `union`, `intersect`, and `minus`

Binary operators at the same precedence level are left-associative.

For example:

```text
A union B minus C
```

is interpreted as:

```text
(A union B) minus C
```

while:

```text
R union S times T
```

is interpreted as:

```text
R union (S times T)
```

---

## Tokenizer

The tokenizer is implemented manually and scans the source code character by character. It does not use regular expressions, parser generators, `eval`, or `exec`.

It currently recognizes:

- Identifiers
- Numbers
- Negative numbers
- Quoted strings
- Bare strings in relation data
- Parentheses
- Braces
- Brackets
- Commas
- Dots
- Comparison operators
- Significant newlines in relation definitions
- `//` comments
- End-of-file

### Maximal Munch

Multi-character comparison operators are recognized using maximal munch.

For example:

```text
Age>=30
```

produces `>=` as one comparison operator.

However:

```text
Age>-30
```

produces `>` and `-30` separately. There is no `>-` operator.

### Strings

Quoted strings use single quotes:

```text
'John Smith'
```

Characters such as commas and parentheses are allowed inside quoted strings:

```text
'a,b'
'Bob)'
```

A doubled single quote represents a literal quote:

```text
'O''Brien'
```

which is tokenized with the string value:

```text
O'Brien
```

### Bare Relation Values

Unquoted values inside relation definitions are scanned as complete values before being classified.

For example:

```text
123
```

is a number, while:

```text
123abc
```

is one bare string rather than a number followed by another token.

### Keywords

Keywords are not given separate token types.

Words such as:

```text
select
project
union
and
or
```

are initially tokenized as identifiers. The parser will interpret them according to their grammatical context.

This allows expressions such as:

```text
select[union=3](R)
```

where `union` is being used as an attribute name.

---

## Source Positions and Errors

Every token stores its source position:

- Character index
- Line
- Column

Indexes are zero-based, while line and column numbers are one-based.

Invalid characters produce a lexical error containing the source position.

For example, because identifiers must begin with an ASCII letter:

```text
_Employee
```

produces a lexical error at line 1, column 1.

Similarly, an unterminated string such as:

```text
select[Name='Bob](R)
```

produces a lexical error pointing to the opening quote.

The tokenizer only handles lexical validity. Grammatically invalid token sequences are left for the parser.

For example:

```text
select[Age=](R)
```

can be tokenized successfully but will eventually be rejected by the parser because the comparison is missing its right-hand operand.

---

## Project Structure

```text
Relational-Algebra-Engine/
├── docs/
├── generator/
├── src/
│   ├── engine/
│   ├── lexer/
│   │   ├── __init__.py
│   │   ├── token.py
│   │   └── tokenizer.py
│   └── parser/
├── tests/
│   └── test_tokenizer.py
├── DESIGN_LOG.md
├── GRAMMAR.md
└── README.md
```

### `src/lexer/token.py`

Defines:

- `TokenType`
- `SourcePosition`
- `Token`

### `src/lexer/tokenizer.py`

Contains the hand-written tokenizer and `LexicalError`.

### `src/parser/`

Reserved for the recursive-descent parser and AST implementation.

### `src/engine/`

Reserved for relational algebra evaluation and semantic processing.

### `GRAMMAR.md`

Contains the EBNF grammar, precedence and associativity rules, ambiguity analysis, parsing strategy, and grammar-design notes.

### `DESIGN_LOG.md`

Documents development decisions, problems encountered, testing, and AI assistance throughout the project.

---

## Testing

The tokenizer is tested using `pytest`.

### Set Up the Virtual Environment

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install pytest:

```bash
python3 -m pip install pytest
```

### Run the Tests

From the project root:

```bash
python3 -m pytest
```

Current tokenizer test status:

```text
16 passed
```

The test suite contains all nine required tokenizer cases as well as regression tests for issues discovered during development.

Current regression coverage includes:

- Alphanumeric bare relation values such as `123abc`
- Quoted-only relation tuples
- Comment-only lines
- Inline comments without preceding whitespace
- Non-ASCII identifiers
- Identifiers beginning with `_`
- Standalone `!`

---

## Parsing Strategy

The parser will use recursive descent.

The grammar has been structured into precedence levels so that each level can map naturally to a parsing function.

Relational expressions follow the general structure:

```text
parseExpr
    → parseSetExpr
        → parseProductExpr
            → parsePrimaryExpr
```

Conditions similarly use separate parsing levels for:

```text
or
and
not
comparison
```

Left recursion was removed from the grammar so that the recursive-descent parser always consumes input before recursively processing additional expressions.

---

## Next Steps

The next development phase is the AST and recursive-descent parser.

The AST and parser will need to represent:

- Relation references
- Selection
- Projection
- Rename
- Union
- Intersection
- Difference
- Cartesian product
- Theta join
- Comparisons
- Boolean `not`
- Boolean `and`
- Boolean `or`

After parsing is complete, development will move to semantic validation and execution of relational algebra expressions.