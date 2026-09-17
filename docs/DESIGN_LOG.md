# Design Log

## September 14, 2026 — Relational Algebra Preparation

### Goal

Before beginning the relational algebra query processor, I wanted to make sure I understood the relational algebra operations that the engine will need to support.

### What I Did

I practiced writing relational algebra queries using selection (`σ`), projection (`π`), joins (`⋈`), union (`∪`), intersection (`∩`), difference (`−`), and rename (`ρ`). I also practiced nested expressions, self-joins, Boolean conditions using `and`, `or`, and `not`, and comparisons involving dates.

I worked through queries involving multiple conditions and learned how parentheses and Boolean operators affect the meaning of selection conditions. I also practiced using rename when two relations need compatible attribute names for set operations and when a relation needs to participate in a self-join.

### What I Learned

The order and grouping of operations are important because changing the structure of a relational algebra expression can change its result. I also learned that schemas matter for operations such as union, intersection, difference, joins, and self-joins.

This preparation gave me a better understanding of the operations that the query processor will eventually need to represent, parse, and execute.

### Problems / AI Assistance

During practice, AI feedback helped identify mistakes in some of my relational algebra expressions, especially Boolean conditions involving `not`, `and`, and `or`. This showed me that expressions that look similar can have different meanings depending on their grouping. I verified corrections by working through the conditions and determining which tuples should satisfy them rather than relying only on the suggested answer.

## September 15, 2026 — Grammar Design

### Goal

My goal was to define the complete EBNF grammar for the relational algebra language before beginning the tokenizer or parser. I also needed to decide operator precedence and associativity, demonstrate ambiguity in a naive grammar, and choose a parsing strategy.

### What I Did

I defined lexical rules for identifiers, numbers, quoted strings, bare strings, and relation definitions. I then created grammar rules for `select`, `project`, `rename`, `union`, `intersect`, `minus`, `times`, and theta joins.

I separated relational expressions into precedence levels using `SET_EXPR`, `PRODUCT_EXPR`, and `PRIMARY_EXPR`. I also separated conditions into `OR_CONDITION`, `AND_CONDITION`, `NOT_CONDITION`, and `COMPARISON` so that comparisons bind tighter than `not`, which binds tighter than `and`, which binds tighter than `or`.

I chose left associativity for `union`, `intersect`, `minus`, `times`, and `join`, and right associativity for repeated `not`. I also chose recursive descent as the parsing strategy and structured the grammar to avoid left recursion.

For `project[Name, Name](R)`, I decided that the expression is syntactically valid but will produce a semantic error because duplicate attributes are not allowed in a projection list.

### What I Learned

I learned that ambiguity and associativity have to be decided by the grammar rather than handled as special cases in the parser. For example, my grammar makes:

`A union B minus C`

group as:

`(A union B) minus C`

and:

`A minus B minus C`

group as:

`(A minus B) minus C`.

I also learned why a directly left-recursive rule such as:

`Expr ::= Expr "union" Expr`

does not work with a recursive-descent parser. The parser could recursively call itself without consuming any input. Using EBNF repetition after first parsing an operand avoids this problem and also provides a natural way to construct left-associative expressions.

### Problems / AI Assistance

There were three specific cases where AI assistance was incorrect or incomplete during the grammar design.

1. While creating the ambiguity demonstration, AI initially suggested `A = {1}`, `B = {2}`, and `C = {2}` for `A union B minus C`. I manually evaluated both parse trees and found that they both produced `{1}`, so the example did not actually demonstrate ambiguity affecting the result. I changed `C` to `{1}`, which makes `(A union B) minus C = {2}` while `A union (B minus C) = {1, 2}`.

2. An earlier AI-assisted version of the grammar only allowed `NUMBER` and quoted `STRING` values in relation definitions. Comparing this with the assignment examples showed that values such as `E1`, `John`, and `D1` also need to work without quotes. I corrected this by adding a `BARE_STRING` token and allowing it in `RELATION_VALUE`.

3. AI initially suggested constructing `BARE_STRING` using `LETTER` and `NUMBER`. I noticed that this was incorrect because `NUMBER` represents a complete numeric token such as `42` or `-7`, not a single character. I corrected the grammar by defining `BARE_STRING_CHAR` separately and then defining `BARE_STRING` as one or more of those characters.

## September 16/17, 2026 — Tokenizer Implementation and Testing

### Goal

Implement the tokenizer based on the lexical rules defined in `GRAMMAR.md` and verify that it correctly converts the input language into tokens before beginning the parser.

### What I Did

I implemented a hand-written tokenizer that scans the source character by character without using regular expressions or parser-generation libraries. The tokenizer tracks the index, line, and column of each token so lexical errors can report their source position.

I added support for identifiers, numbers, quoted strings, bare strings, punctuation, comparison operators, comments, and significant newlines inside relation definitions. Comparison operators use maximal munch so operators such as `>=`, `<=`, and `!=` are emitted as single tokens, while an expression such as `Age>-30` produces `>` and `-30` separately.

Keywords such as `select`, `union`, and `and` are tokenized as identifiers. Their meaning will be determined later by the parser based on context. This also allows a keyword to be used as an attribute name where the grammar permits it.

Relation data required additional tokenizer state because newlines are significant between tuples but normally ignored elsewhere. I used `inside_relation_data` and `line_has_data` to distinguish tuple-ending newlines from blank or comment-only lines.

### What I Learned

The tokenizer should only determine whether the source characters can be converted into valid tokens. It should not decide whether those tokens form a grammatically valid expression. For example, `select[Age=](R)` can be tokenized successfully, but the parser must later reject it because the comparison is missing its right operand.

I also learned that tokenization rules sometimes depend on context. Inside relation data, an unquoted value must be scanned completely before it is classified. For example, `123abc` must become one `BARE_STRING` rather than `NUMBER("123")` followed by another token.

The tokenizer must also follow the lexical grammar exactly. Python methods such as `isalpha()` and `isdigit()` accept Unicode characters, while my grammar defines letters and digits as ASCII `A-Z`, `a-z`, and `0-9`. I therefore implemented explicit ASCII checks.

### Problems / AI Assistance

During implementation, AI initially suggested logic for detecting `//` comments while scanning a bare relation value that used the wrong lookahead position. Testing `D1//comment` exposed the problem because the comment marker was being consumed as part of the bare string. I corrected this by checking the two characters beginning at the tokenizer's current position before continuing to scan the value.

Another issue appeared with a relation containing a tuple made entirely from a quoted string. The tokenizer initially failed to emit the tuple's terminating `NEWLINE` because scanning a string did not mark the line as containing relation data. I fixed this by setting `line_has_data` after a string is successfully scanned inside relation data and added a regression test for the case.

The initial implementation also used Python's `isalpha()`, `isalnum()`, and `isdigit()` methods. Comparing this implementation against my grammar showed that these methods accept characters outside the grammar's ASCII definition. I replaced them with explicit ASCII letter and digit checks and verified the change with a non-ASCII identifier test.

### Testing

I implemented all nine required tokenizer tests from the project specification. These cover whitespace handling, maximal-munch comparison operators, negative numbers, punctuation inside quoted strings, commas inside strings, doubled quotes, keywords used as attributes, and unterminated strings with source positions.

I also added regression tests for issues discovered during development, including alphanumeric bare relation values, quoted-only tuples, comment-only lines, inline comments without whitespace, non-ASCII identifiers, identifiers beginning with an underscore, and standalone `!`.

At the end of this session, the tokenizer test suite contained 16 tests and all 16 passed.