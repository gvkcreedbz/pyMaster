# Day 29 — Capstone: Build a Sales Data Pipeline (ETL)

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h (+ optional extra) | Combine 4 weeks of skills into one command-line tool that turns a messy CSV into a clean database, a report and a chart | Upper-intermediate |

## 🌍 Real-world scenario & trend
**Every Monday the store emails `sales_messy.csv`.** Your manager wants: a cleaned database, a one-page report, and a chart — *without you repeating 40 manual steps*. That is a **data pipeline**: **E**xtract → **T**ransform → **L**oad → **R**eport. **Trend:** this exact shape powers data engineering (Airflow, dbt), analytics reports and ML feature pipelines. Being able to build, test and run one end-to-end is a portfolio-grade skill.

## 0. Warm-up (5 min) — Day 28 recap
- Why use `?` placeholders?  • What does `with conn:` do on error?

## 1. The architecture
```
sales_messy.csv ──extract──▶ raw DataFrame ──quality_report──▶ (log the problems)
                                   │
                                transform (clean + revenue)
                                   │
              ┌────────────────────┼─────────────────────┐
         load_to_sqlite         kpis ──write_report     save_chart
         (sales.db)             (report.md)             (revenue_by_region.png)
```
**One function = one job.** `run_pipeline()` only calls them in order; `main()` only parses the command line. That makes every piece testable (Day 24) and replaceable.

## 2. Toolkit refresher (all from earlier days)
| Need | Tool | Day |
|---|---|---|
| paths that work everywhere | `pathlib.Path`, `mkdir(parents=True, exist_ok=True)` | 15 |
| friendly failures | `try/except`, `FileNotFoundError`, `raise` | 17 |
| progress messages | `logging.getLogger(__name__).info(...)` | 17 |
| cleaning & KPIs | pandas `drop_duplicates`, `str.strip().str.title()`, `groupby` | 25–26 |
| storage | `df.to_sql(...)`, `sqlite3` | 28 |
| command line | `argparse` | below |
| quality | type hints, small functions, tests | 23–24 |

### 2.1 `argparse` — turn a script into a tool
```python
import argparse

def main(argv=None):
    parser = argparse.ArgumentParser(description="Clean the weekly sales export.")
    parser.add_argument("--input", required=True, help="path to the messy CSV")
    parser.add_argument("--out", default="output", help="folder for the results")
    args = parser.parse_args(argv)           # argv=None -> reads the real command line
    ...
    return 0                                  # exit code: 0 = success, non-zero = failure

if __name__ == "__main__":
    raise SystemExit(main())
```
Run: `python sales_pipeline.py --input datasets/sales_messy.csv --out output` · `--help` is free!

### 2.2 `to_sql` in one line
```python
df.to_sql("orders", conn, if_exists="replace", index=False)
```
Convert dates to text first (`df["order_date"].dt.strftime("%Y-%m-%d")`) — SQLite has no real date type.

### 2.3 A good README (what employers read first)
Title · what problem it solves · how to run it (copy-paste commands) · sample output/screenshot · design (the diagram above) · what you'd improve next.

## 3. Code along → `examples.py`
It runs the finished pipeline on the messy file and prints the report. Read it **after** attempting the practice, or use it as a reference for structure.

## 4. Common mistakes
- One giant 200-line function; hidden global variables.
- Cleaning and reporting on **different** data (always pass the cleaned DataFrame forward).
- Overwriting the raw input file — **never** modify the source; write results to a separate `output/` folder.
- No validation numbers: always log rows before/after and the revenue total, so a silent bug is visible.
- Forgetting the exit code → schedulers can't tell that your job failed.

## 5. Today's tasks → `practice.py`
You'll write the pieces in order — reuse your Day 26 code freely!
| ID | Level | Task |
|---|---|---|
| L1-1, L1-2 | 🟢 | `extract`, `quality_report` |
| L2-1…L2-3 | 🟡 | `transform`, `load_to_sqlite`, `kpis` |
| L3-1…L3-3 | 🔴 | `write_report`, `run_pipeline` (files + errors), `main` with `argparse` |

## 6. Stuck? Hint ladder
<details><summary>Hint 1</summary>Test each function alone in a scratch file with the real CSV before wiring them together. Print <code>df.shape</code> after each step.</details>
<details><summary>Hint 2</summary><code>transform</code> is your Day 26 <code>clean_sales</code> plus a revenue column. KPIs: <code>df.groupby("region")["revenue"].sum().idxmax()</code> gives the best region. Report numbers with thousands separators: <code>f"{value:,.2f}"</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day29_solution.py</code></details>

## 7. Stretch goals (after the checks pass, if you have time/energy)
1. Turn `practice.py` into a standalone `sales_pipeline.py` + a `README.md`; run `ruff check .`.
2. Write 5 pytest tests for `transform` and `kpis` (use a tiny hand-made DataFrame).
3. Add a `--month 2026-06` filter option.
4. Push the project to GitHub (`.gitignore` the `output/` folder!).
5. Schedule it weekly (Windows Task Scheduler / cron).
6. Ask an LLM to *review* your code — then **you** decide which suggestions are right (that's the skill).

## 8. Quiz — answers in `solutions/day29_answers.md`
1. What do E, T, L stand for?
2. Why should `main()` return an exit code?
3. Why never overwrite the raw input file?
4. What does `if __name__ == "__main__":` do?
5. Why keep functions small and single-purpose?
6. How do you make a pipeline's problems visible?
7. What does `parse_args(argv)` do when `argv=None`?
8. Name two ways to test a pipeline.

## 9. Wrap-up
Tracker + Bug Journal. Tomorrow: a taste of **FastAPI** (turn your pipeline's data into a web API) and the **final exam**.
