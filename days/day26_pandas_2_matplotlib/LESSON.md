# Day 26 — pandas II: Cleaning, groupby, merge, pivot & Charts

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Turn a messy export into trustworthy numbers, summarise it, and plot it | Upper-intermediate |

## 🌍 Real-world scenario & trend
**Monday morning, a "fresh export" arrives — `datasets/sales_messy.csv`:** `" SOUTH "`, `"grocery "`, prices like `"1,999"`, blanks, and 8 duplicated rows. If you analyse it as-is, every total is wrong. **Trend:** data analysts and ML engineers spend ~60–80% of their time cleaning data; the habit *"inspect → clean → validate → analyse"* is what separates trustworthy results from confident nonsense. Charts then turn numbers into decisions.

## 0. Warm-up (5 min) — Day 25 recap
- Filter rows where `quantity >= 5` and region is West.  • What does `df.info()` show?

## 1. Setup (3 min)
```powershell
python -m pip install pandas matplotlib
```

## 2. Concepts

### 2.1 Inspect before you clean
```python
df = pd.read_csv("datasets/sales_messy.csv")
df.shape; df.info(); df.isna().sum()          # missing values per column
df["region"].unique()                         # reveals ' south', 'SOUTH ', 'south' ...
df.duplicated().sum()                         # how many fully duplicated rows
```

### 2.2 Cleaning toolbox
```python
df = df.drop_duplicates()                                   # remove duplicate rows
df["region"] = df["region"].str.strip().str.title()         # ' SOUTH ' -> 'South'
df["unit_price"] = df["unit_price"].astype(str).str.replace(",", "").astype(int)   # '1,999' -> 1999
df["discount_pct"] = df["discount_pct"].fillna(0)           # fill blanks with a sensible default
df = df.dropna(subset=["quantity"])                         # drop rows missing a critical value
df["quantity"] = df["quantity"].astype(int)
df["order_date"] = pd.to_datetime(df["order_date"])
df = df.reset_index(drop=True)
```
**Decision log:** *fill* when a sensible default exists (no discount = 0), *drop* when guessing would invent data (unknown quantity). Always write down what you did.

### 2.3 groupby + agg — the heart of analysis
```python
df.groupby("category")["revenue"].sum()
df.groupby("category").agg(orders=("order_id", "count"), revenue=("revenue", "sum"), avg_qty=("quantity", "mean"))
df.groupby(["region", "category"])["revenue"].sum()        # two keys -> multi-index
.reset_index()                                             # turn the group keys back into columns
```

### 2.4 `pivot_table` — Excel pivot in one line
```python
df.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", fill_value=0)
```

### 2.5 `merge` — SQL-style join of two tables
```python
targets = pd.DataFrame({"region": ["East", "West"], "target": [300000, 400000]})
combined = revenue_by_region.merge(targets, on="region", how="left")     # how: inner / left / right / outer
combined["achieved_pct"] = combined["revenue"] / combined["target"] * 100
```

### 2.6 Charts with matplotlib
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 4))
revenue_by_region.plot(kind="bar", ax=ax, color="steelblue")      # pandas plots through matplotlib
ax.set_title("Revenue by region"); ax.set_xlabel("Region"); ax.set_ylabel("Revenue (₹)")
fig.tight_layout()
fig.savefig("regions.png", dpi=120)       # save a file ...
plt.show()                                # ... or open a window
plt.close(fig)
```
Pick the right chart: **bar** = compare categories · **line** = trend over time · **histogram** = distribution · **scatter** = relationship between two numbers · **pie** = almost never.
Every chart needs: a title, labelled axes, and a message you can say in one sentence.

## 3. Code along → `examples.py` (cleans the messy file, summarises it, saves 2 PNG charts in `output/`)

## 4. Common mistakes
- Cleaning without looking first (`unique()`, `isna()`), or without validating after (row counts, totals).
- `groupby(...).sum()` on text columns, or forgetting `["col"]` and summing everything.
- Using `merge` with different key spellings (`"east"` vs `"East"`) → silent NaNs. Clean keys first!
- Treating `NaN` like a normal number (`NaN == NaN` is False; use `.isna()`).
- Pie charts with 12 slices; unlabeled axes; truncated y-axes that exaggerate differences.

## 5. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Strip/title text, count missing values, drop duplicates |
| L2-1…L2-3 | 🟡 | Fix `"1,999"` prices, full `clean_sales` pipeline, category summary with `agg` |
| L3-1…L3-3 | 🔴 | Region vs target (`merge`), save a bar chart PNG, region × category pivot |

## 6. Stuck? Hint ladder
<details><summary>Hint 1</summary>Print after each cleaning step: <code>print(df.shape, df.isna().sum().sum())</code>. Do one step per line; don't chain everything blind.</details>
<details><summary>Hint 2</summary>Prices: <code>.astype(str).str.replace(",", "").astype(int)</code>. Missing: <code>df.isna().sum()</code> then keep only counts &gt; 0. Merge: <code>left.merge(right, on="region")</code>. Chart: <code>ax.bar(x, heights)</code> then <code>fig.savefig(path)</code>; remember <code>plt.close(fig)</code>.</details>
<details><summary>Hint 3</summary><code>solutions/day26_solution.py</code></details>

## 7. Quiz — answers in `solutions/day26_answers.md`
1. Why inspect data before cleaning?
2. When should you fill missing values and when drop them?
3. What does `.str.strip().str.title()` do to `" sOUTH "`?
4. What does `groupby("a").agg(n=("b", "count"))` return?
5. When do you pick `how="left"` in a merge?
6. Name the right chart for: trend over time; comparing 4 regions; distribution of order values.
7. What does `plt.close(fig)` prevent?
8. Why can a `merge` silently produce `NaN`s?

## 8. Wrap-up
Tracker + Bug Journal. Tomorrow: APIs & web scraping — getting data from the internet.
