# Day 24 — Quiz answers

1. Files named `test_*.py` (or `*_test.py`) containing functions named `test_*` (and classes `Test*`).
2. It raises `AssertionError`; pytest marks that test as failed and shows the values it compared.
3. `with pytest.raises(ValueError): function(bad_input)`.
4. Copy-pasting the same test many times — one test function runs against a whole table of inputs/expected outputs and reports each case separately.
5. A function decorated with `@pytest.fixture` that prepares shared setup (a fresh object, a temp file, a DB connection). Tests receive it by naming it as a parameter.
6. Floats are inexact (`0.1 + 0.2 != 0.3`); `pytest.approx(0.3)` compares within a small tolerance.
7. `git add` stages (selects) changes; `git commit` saves the staged snapshot to history.
8. To keep generated files, virtual environments and secrets (`.env`, API keys) out of the repository.
