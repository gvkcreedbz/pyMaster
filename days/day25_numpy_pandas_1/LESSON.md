# Day 25 — NumPy & pandas I: Arrays and DataFrames

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Load a real sales file, add columns, filter, sort and summarise it with a few lines of pandas | Upper-intermediate |

## 🌍 Real-world scenario & trend
**You're the new analyst at an online store.** The boss drops `datasets/sales.csv` (300 orders) on your desk: *"Which region earns most? Which products carry the business?"* Excel can do it, but pandas does it for 300 **million** rows, repeatably. **Trend:** pandas + NumPy underpin virtually all data science and ML (scikit-learn, PyTorch and LLM data pipelines all speak NumPy arrays or DataFrames). Newer alternatives (Polars, DuckDB) copy the same ideas, so learn the concepts once.

## 0. Warm-up (5 min) — Day 24 recap
- What does `assert` do?  • What makes a pytest test discoverable?

## 1. Setup (3 min)
```powershell
python -m pip install numpy pandas
```
(or `python -m pip install -r requirements-week4.txt`). Use the same Python that runs your scripts: `python -m pip ...`.

## 2. Concepts

### 2.1 NumPy: fast arrays and "vectorised" maths
```python
import numpy as np
temps_c = np.array([22.5, 30.1, 18.0, 35.2])
temps_f = temps_c * 9 / 5 + 32          # whole array at once - no loop!
temps_c.mean(), temps_c.max(), temps_c.std()
temps_c[temps_c > 25]                   # boolean mask -> array([30.1, 35.2])
np.arange(0, 10, 2)                     # [0 2 4 6 8]
np.zeros((2, 3)); np.ones(3); np.linspace(0, 1, 5)
grid = np.array([[1, 2, 3], [4, 5, 6]])
grid.shape                              # (2, 3)
grid.sum(axis=0), grid.sum(axis=1)      # per column / per row -> [5 7 9] [ 6 15]
grid[:, 1]                              # second column -> [2 5]
```
Why faster than lists? One typed block of memory + C loops. `array * 2` multiplies *every* element (a list would repeat itself!). **Broadcasting**: `grid + np.array([10, 20, 30])` adds to each row.

### 2.2 pandas: `Series` (a column) and `DataFrame` (a table)
```python
import pandas as pd
df = pd.read_csv("datasets/sales.csv", parse_dates=["order_date"])
df.shape            # (300, 9)
df.head()           # first 5 rows;  df.tail(3)
df.info()           # columns, types, missing values
df.describe()       # count/mean/min/max of numeric columns
df.columns, df.dtypes
```

### 2.3 Selecting
```python
df["region"]                      # one column (Series)
df[["product", "quantity"]]       # several columns (DataFrame)
df.iloc[0]                        # row by position
df.loc[0, "product"]              # label-based: row label 0, column "product"
df.loc[df["quantity"] > 3, ["product", "quantity"]]   # rows by condition + chosen columns
```

### 2.4 Filtering with boolean masks (use `&`, `|`, `~` with brackets!)
```python
west_big = df[(df["region"] == "West") & (df["quantity"] >= 5)]
cards = df[df["payment_method"].isin(["Card", "UPI"])]
df[df["product"].str.contains("Phone")]
```

### 2.5 New columns, sorting, counting
```python
df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
df.sort_values("revenue", ascending=False).head(5)
df["region"].value_counts()          # how many rows per region
df["revenue"].sum(), df["revenue"].mean(), df["revenue"].nlargest(3)
df["order_date"].dt.month            # date parts via the .dt accessor
```

### 2.6 The golden rule
**Don't write `for` loops over rows.** Use column maths, masks and (tomorrow) `groupby`. Loops are 100× slower and 5× longer.

### 2.7 SettingWithCopy & copies
`df2 = df[df.region == "West"].copy()` — call `.copy()` before modifying a filtered table. Most pandas methods **return a new object**; they don't change `df` unless you assign the result.

### 2.8 Sneak preview: `groupby` ("split → add up → combine")
```python
df.groupby("region")["revenue"].sum()            # total revenue per region (a Series)
df.groupby("region")["revenue"].sum().round(2).to_dict()     # -> {'East': 335268.6, ...}
df.groupby("product")["revenue"].sum().nlargest(3)           # top 3 products
df.groupby(df["order_date"].dt.to_period("M").astype(str))["revenue"].sum()   # per month
```
Read it aloud: *"group the rows by region, take the revenue column, sum it."* Tomorrow we master it.

## 3. Code along → `examples.py`

## 4. Common mistakes
- `df[df.a > 1 and df.b < 5]` → use `&` and wrap each condition in `( )`.
- Forgetting `.copy()`, or expecting `df.sort_values(...)` to sort `df` in place.
- Using `df["col"]` vs `df.col` interchangeably — column names with spaces/clashes break `df.col`.
- Looping with `iterrows` for maths.
- Mixing up `loc` (labels, inclusive end) and `iloc` (positions, exclusive end).

## 5. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | °C→°F arrays, values above average (mask), load the CSV |
| L2-1…L2-3 | 🟡 | Add a `revenue` column, top-selling products, filter orders |
| L3-1, L3-2 | 🔴 | Revenue by region, revenue by month (use the `groupby` preview in 2.8) |

## 6. Stuck? Hint ladder
<details><summary>Hint 1</summary>Print intermediate results: <code>print(df.head())</code>, <code>print(df.dtypes)</code>. Work column-wise, not row-wise.</details>
<details><summary>Hint 2</summary>Revenue by region: <code>df.groupby("region")["revenue"].sum()</code>. Monthly: group by <code>df["order_date"].dt.to_period("M").astype(str)</code>. Convert results with <code>.round(2).to_dict()</code>. Top products: <code>.nlargest(n).index</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day25_solution.py</code></details>

## 7. Quiz — answers in `solutions/day25_answers.md`
1. Why is `np.array([1,2,3]) * 2` different from `[1,2,3] * 2`?
2. What does `axis=0` mean in `arr.sum(axis=0)`?
3. How do you keep rows where quantity ≥ 5 **and** region is West?
4. Difference between `loc` and `iloc`?
5. What does `df.describe()` show?
6. Why `.copy()` after filtering?
7. How do you get row counts per category?
8. Why avoid `for` loops over DataFrame rows?

## 8. Wrap-up
Tracker + Bug Journal. Tomorrow: groupby, merging, cleaning messy data, and charts.
