# 🎓 Day 30 — FINAL EXAM (45 minutes, closed-book)

**Rules:** do NOT run the code, do NOT use AI or notes. Read each snippet carefully and write down exactly what it prints (or the error it raises). 1 point each → **27 points**. Questions are in a deliberate mix of topics; the *Day* tag tells you which lesson to revisit if you miss it.

> Tip: trace variables on paper. Exact output counts — spaces, brackets and quotes matter.

After finishing, check `solutions/day30_exam_answers.md`, write your score in the tracker and note your weak topics.

---

### Q1. (Day 3) — numbers & strings
```python
print(7 // 2, 7 % 2, 7 / 2, 2 ** 3, "ab" * 2)
```
**Your answer:** ______________________

### Q2. (Day 4) — string slicing
```python
s = "Python Rocks"
print(s[::-1][:4], s.lower().count("o"), s.split()[1][0])
```
**Your answer:** ______________________

### Q3. (Day 5) — truthiness
```python
print(bool(""), bool("0"), bool([]), bool([0]), None == False)
```
**Your answer:** ______________________

### Q4. (Day 6) — range & loops
```python
for i in range(10, 0, -3):
    print(i, end=" ")
```
**Your answer:** ______________________

### Q5. (Day 6) — loop with else
```python
for n in [4, 8, 9]:
    if n % 2 == 1:
        print("odd found:", n)
        break
else:
    print("all even")
```
**Your answer:** ______________________

### Q6. (Day 8) — list aliasing
```python
a = [1, 2, 3]
b = a
c = a[:]
b.append(4)
print(a, c)
```
**Your answer:** ______________________

### Q7. (Day 8) — list methods
```python
nums = [5, 3, 8, 1]
print(sorted(nums)[-2:], nums.pop(1), nums)
```
**Your answer:** ______________________

### Q8. (Day 10) — dictionary counting
```python
d = {}
for w in "a b a c b a".split():
    d[w] = d.get(w, 0) + 1
print(d, max(d, key=d.get))
```
**Your answer:** ______________________

### Q9. (Day 9) — sets
```python
print({1, 2, 3} & {2, 3, 4}, {1, 2} | {2, 5}, len({1, 1, 2}))
```
**Your answer:** ______________________

### Q10. (Day 11) — mutable default argument
```python
def add(x, bucket=[]):
    bucket.append(x)
    return bucket

print(add(1), add(2))
```
**Your answer:** ______________________

### Q11. (Day 11) — *args and **kwargs
```python
def f(a, *args, **kw):
    return a, args, kw

print(f(1, 2, 3, k=4))
```
**Your answer:** ______________________

### Q12. (Day 12) — comprehensions
```python
print([x * x for x in range(6) if x % 2 == 0], {w: len(w) for w in ["hi", "python"]}, sum(x for x in range(4)))
```
**Your answer:** ______________________

### Q13. (Day 12) — sorting with lambda
```python
people = [("Ann", 30), ("Bob", 25), ("Cy", 30)]
print(sorted(people, key=lambda p: (-p[1], p[0])))
```
**Your answer:** ______________________

### Q14. (Day 17) — try / finally
```python
def f():
    try:
        return "try"
    finally:
        print("cleanup")

print(f())
```
**Your answer:** ______________________

### Q15. (Day 17) — exception flow
```python
try:
    int("x")
except ZeroDivisionError:
    print("zero")
except ValueError:
    print("value")
else:
    print("else")
finally:
    print("done")
```
**Your answer:** ______________________

### Q16. (Day 19) — classes & inheritance
```python
class Animal:
    sound = "..."
    def __init__(self, name):
        self.name = name
    def speak(self):
        return f"{self.name} says {self.sound}"

class Dog(Animal):
    sound = "Woof"

print(Dog("Rex").speak(), "|", Animal("Tom").speak())
```
**Your answer:** ______________________

### Q17. (Day 22) — generators
```python
def gen():
    for i in range(3):
        yield i * i

g = gen()
print(next(g), next(g), list(g), list(g))
```
**Your answer:** ______________________

### Q18. (Day 22) — decorators
```python
def twice(f):
    def wrapper(*a):
        return f(*a) * 2
    return wrapper

@twice
def add(a, b):
    return a + b

print(add(2, 3))
```
**Your answer:** ______________________

### Q19. (Day 23) — regex
```python
import re
print(re.findall(r"\d+", "a1b22c333"), re.sub(r"\s+", " ", "a   b \n c"))
```
**Your answer:** ______________________

### Q20. (Day 26) — pandas groupby
```python
import pandas as pd
df = pd.DataFrame({"city": ["A", "B", "A", "B", "A"], "sales": [10, 20, 30, 40, 50]})
print(df.groupby("city")["sales"].sum().to_dict(), df[df.sales > 20].shape)
```
**Your answer:** ______________________

### Q21. (Day 28) — SQL
```python
import sqlite3
c = sqlite3.connect(":memory:")
c.execute("create table t(x int)")
c.executemany("insert into t values(?)", [(1,), (2,), (3,)])
print(c.execute("select sum(x), count(*) from t where x > 1").fetchone())
```
**Your answer:** ______________________

### Q22. (Day 3) — types & conversion
```python
print(type(3 / 1).__name__, type(3 // 1).__name__, "3" + "4", int("3") + int("4"))
```
**Your answer:** ______________________

### Q23. (Day 8) — zip & enumerate
```python
names = ["a", "b"]
ages = [1, 2]
print(list(zip(names, ages)), dict(enumerate(names, 1)))
```
**Your answer:** ______________________

### Q24. (Day 4) — f-string formats
```python
price = 1234.5
print(f"{price:,.2f} | {price:>10.1f} | {0.256:.1%}")
```
**Your answer:** ______________________

### Q25. (Day 6) — BUG: typo operator
```python
total = 0
for p in [10, 20, 30]:
    total =+ p
print(total)
```
**Your answer:** ______________________

### Q26. (Day 10) — BUG: missing key
```python
scores = {"alice": 90}
print(scores["bob"])
```
**Your answer:** ______________________

### Q27. (Day 8) — BUG: changing a list while looping
```python
nums = [1, 2, 2, 3]
for n in nums:
    if n == 2:
        nums.remove(n)
print(nums)
```
**Your answer:** ______________________
