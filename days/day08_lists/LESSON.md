# Day 08 — Lists

| ⏱ Time | 🎯 Goal | 🏁 Level |
|---|---|---|
| 2 h | Store, change, search, sort and loop over collections of items | Beginner+ |

## 🌍 Real-world scenario & trend
**A shopping cart, a Spotify playlist, a to-do app.** Anything “many of the same kind” is a list: cart items, search results, 10,000 sensor readings. **Trend:** in data/AI work, a list is the raw form of a column of data — pandas, NumPy and ML libraries all start from lists.

## 0. Warm-up (5 min) — Day 07 recap
- What does `while True:` + `break` do?  • What does `"a,b".split(",")` return?

## 1. Concepts

### 1.1 Create, index, slice (same rules as strings)
```python
cart = ["milk", "bread", "eggs"]
cart[0]         # 'milk'      cart[-1]   # 'eggs'
cart[1:]        # ['bread', 'eggs']      len(cart)  # 3
```

### 1.2 Lists are **mutable** (they can change)
```python
cart[1] = "brown bread"        # replace
cart.append("butter")          # add at the end
cart.insert(0, "tea")          # add at a position
cart.extend(["jam", "salt"])   # add many
cart.remove("eggs")            # remove by value (first match)
last = cart.pop()              # remove & return the last item (cart.pop(0) = first)
del cart[0]                    # remove by index
```

### 1.3 Useful tools
```python
nums = [5, 2, 9, 1]
sum(nums), min(nums), max(nums), len(nums)   # 17 1 9 4
sorted(nums)            # NEW sorted list [1,2,5,9], original unchanged
nums.sort()             # sorts IN PLACE (returns None!)
nums.sort(reverse=True) # descending
nums.reverse()
9 in nums               # True      nums.count(2)  # 1     nums.index(9) # position
```

### 1.4 Looping
```python
for item in cart:
    print(item)
for i, item in enumerate(cart, start=1):    # position + value
    print(i, item)
```

### 1.5 The copy trap (very common bug)
```python
a = [1, 2, 3]
b = a            # NOT a copy: both names point to the SAME list
b.append(4)
print(a)         # [1, 2, 3, 4]  <- surprise
c = a.copy()     # or a[:] or list(a)  -> a real copy
```

### 1.6 Lists of lists (a table) and unpacking
```python
grid = [[1, 2], [3, 4]]
grid[1][0]                     # 3
first, second, *rest = [10, 20, 30, 40]   # 10 20 [30, 40]
```

## 2. Code along → `examples.py` (cart + leaderboard)

## 3. Common mistakes
- `nums = nums.sort()` → `nums` becomes `None` (sort returns nothing).
- Changing a list while looping over it (skips items) — loop over a copy or build a new list.
- `IndexError`: using an index ≥ `len(list)`.
- `append` adds ONE item; `extend` adds many (`append([1,2])` nests a list).

## 4. Today's tasks → `practice.py`
| ID | Level | Task |
|---|---|---|
| L1-1…L1-3 | 🟢 | Cart total, add without duplicates, top-two scores |
| L2-1…L2-3 | 🟡 | Remove all, trimmed average, running totals |
| L3-1, L3-2 | 🔴 | Rotate a list, merge two sorted lists |

## 5. Stuck? Hint ladder
<details><summary>Hint 1</summary>Try your idea on a 4-item example on paper, tracking the list after each step.</details>
<details><summary>Hint 2</summary>Remove-all: build a <em>new</em> list and append items that differ. Trimmed average: <code>sorted()</code> then slice <code>[1:-1]</code>. Running totals: keep a running <code>total</code> and append it each round. Rotate right by k: use <code>k % len(items)</code> and slicing <code>items[-k:] + items[:-k]</code>. Merge: two index variables <code>i</code>, <code>j</code>; append the smaller; then add the leftovers.</details>
<details><summary>Hint 3</summary><code>solutions/day08_solution.py</code></details>

## 6. Quiz — answers in `solutions/day08_answers.md`
1. `a = [1,2,3]`, `b = a`, `b.append(4)` → what is `a`?
2. What does `nums = [3,1,2]` → `nums = nums.sort()` leave in `nums`?
3. Difference between `append` and `extend`?
4. `[10, 20, 30, 40][1:3]` → ?
5. `pop()` vs `remove(x)` vs `del lst[i]` — one-line difference?
6. What does `sorted(nums)` do to `nums`?
7. What does `[0] * 3` produce?
8. `first, *rest = [1, 2, 3]` → values of `first` and `rest`?

## 7. Wrap-up
Tracker + Bug Journal. Tomorrow: tuples & sets — unique visitors and mutual friends.
