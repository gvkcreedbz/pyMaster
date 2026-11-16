# 📚 Collections & Streams Cheatsheet (Days 8–12, 22, 25–26)

```java
import java.util.*;
import java.util.function.*;
import java.util.stream.*;
```
Collections hold **objects**: write `List<Integer>`, never `List<int>`. Use the **interface** as the variable type: `List<String> xs = new ArrayList<>();`.

## Which one do I pick?
| I need… | Use | Why |
|---|---|---|
| a fixed-size row of values (or primitives) | `int[]` | fastest, simplest |
| an ordered, growable list, duplicates allowed | `ArrayList<T>` | default choice |
| a fixed read-only list | `List.of(a, b, c)` | immutable (no `add`, no `null`) |
| unique items, don't care about order | `HashSet<T>` | fast `contains` |
| unique items, keep insertion order | `LinkedHashSet<T>` | |
| unique items, sorted | `TreeSet<T>` | `first()`, `last()`, `floor()`, `ceiling()` |
| key → value lookup | `HashMap<K,V>` | fast, no order |
| key → value, keep insertion order | `LinkedHashMap<K,V>` | |
| key → value, sorted by key | `TreeMap<K,V>` | `firstKey()`, `headMap()`, `tailMap()` |
| a queue / stack | `ArrayDeque<T>` | `offer/poll/peek`, `push/pop` |

## List
```java
List<String> cart = new ArrayList<>(List.of("tea", "milk"));
cart.add("sugar");  cart.add(0, "rice");  cart.get(1);  cart.set(1, "oil");  cart.size();  cart.isEmpty()
cart.remove("milk");  cart.remove(0);            // by value / by INDEX   (List<Integer>: cart.remove(Integer.valueOf(5)))
cart.contains("tea");  cart.indexOf("tea");  cart.subList(0, 2);  cart.addAll(other);  cart.clear();
Collections.sort(cart);  cart.sort(Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()));
Collections.reverse(cart);  Collections.max(nums);  Collections.min(nums);  Collections.shuffle(cart, new Random(1));  Collections.frequency(cart, "tea");
List<String> copy = new ArrayList<>(cart);       // a real copy;  List<String> alias = cart;  // SAME object
cart.removeIf(s -> s.startsWith("t"));  cart.forEach(System.out::println);  cart.replaceAll(String::toUpperCase);
for (String s : cart) { }                        // never add/remove inside this loop (ConcurrentModificationException)
String[] arr = cart.toArray(new String[0]);      List<Integer> fromArr = Arrays.asList(1, 2, 3);
```

## Set
```java
Set<String> a = new HashSet<>(List.of("x", "y", "z")), b = new HashSet<>(List.of("y", "z", "w"));
a.add("q");  a.remove("x");  a.contains("y");  a.size();         // add returns false if already there
Set<String> both = new HashSet<>(a);   both.retainAll(b);        // intersection  (mutual friends)
Set<String> either = new HashSet<>(a); either.addAll(b);         // union
Set<String> onlyA = new HashSet<>(a);  onlyA.removeAll(b);       // difference
TreeSet<Integer> t = new TreeSet<>(List.of(5, 1, 9));  t.first();  t.last();  t.floor(6);  t.ceiling(6);  t.descendingSet();
```

## Map
```java
Map<String, Integer> stock = new HashMap<>();
stock.put("tea", 10);  stock.get("tea");  stock.get("nope") /* null! */;  stock.getOrDefault("nope", 0);
stock.containsKey("tea");  stock.containsValue(10);  stock.remove("tea");  stock.size();  stock.keySet();  stock.values();  stock.entrySet();
stock.putIfAbsent("rice", 5);
stock.merge("tea", 1, Integer::sum);                           // counting: add 1, or start at 1
stock.computeIfAbsent("k", x -> 0);   stock.compute("k", (k, v) -> v == null ? 1 : v + 1);
Map<String, List<String>> groups = new TreeMap<>();
groups.computeIfAbsent("fruit", k -> new ArrayList<>()).add("apple");   // grouping pattern
for (Map.Entry<String, Integer> e : stock.entrySet()) { e.getKey(); e.getValue(); }
stock.forEach((k, v) -> System.out.println(k + "=" + v));
Map.of("a", 1, "b", 2)                                          // immutable; Map.entry(k, v)
// word count
for (String w : text.toLowerCase().split("\\W+")) counts.merge(w, 1, Integer::sum);
```

## Sorting
```java
people.sort(Comparator.comparing(Person::name));                                  // by one field
people.sort(Comparator.comparingInt(Person::age).reversed());                     // descending
people.sort(Comparator.comparing(Person::city).thenComparing(Person::name));      // tie-breaker
people.sort(Comparator.comparing(Person::name, String.CASE_INSENSITIVE_ORDER));
Map.Entry.<String, Integer>comparingByValue().reversed()                          // sort map entries by value
```

## Stream: source → (zero or more) intermediate steps → one terminal step
```java
list.stream()   Arrays.stream(arr)   Stream.of(1, 2, 3)   IntStream.rangeClosed(1, 5)   Files.lines(path)   map.entrySet().stream()
```
| Step | Kind | Example |
|---|---|---|
| `filter(pred)` | intermediate | `.filter(p -> p.price() > 100)` |
| `map(fn)` | intermediate | `.map(Product::name)` |
| `mapToInt/Double(fn)` | intermediate | `.mapToDouble(Order::total)` |
| `sorted()` / `sorted(cmp)` | intermediate | `.sorted(Comparator.comparing(Order::total).reversed())` |
| `distinct()` · `limit(n)` · `skip(n)` | intermediate | `.sorted(...).limit(3)` (top 3) |
| `flatMap(fn)` | intermediate | `.flatMap(o -> o.items().stream())` |
| `peek(fn)` | intermediate | debugging only |
| `forEach(fn)` | terminal | `.forEach(System.out::println)` |
| `collect(collector)` / `toList()` | terminal | `.toList()` (Java 16+, immutable) |
| `count()` · `sum()` · `average()` · `max()` · `min()` | terminal | `.mapToDouble(...).sum()` |
| `reduce(id, op)` | terminal | `.reduce(0, Integer::sum)` |
| `anyMatch/allMatch/noneMatch(pred)` | terminal | `.anyMatch(x -> x < 0)` |
| `findFirst()` / `findAny()` | terminal → `Optional` | `.findFirst().orElse(null)` |

Primitive streams: `IntStream`/`DoubleStream` have `sum()`, `average()` (→ `OptionalDouble`), `max()`, `summaryStatistics()`. Back to objects: `.boxed()`.
A stream can be used **once**; nothing runs until the terminal step.

## Collectors (`import static java.util.stream.Collectors.*;`)
```java
.collect(Collectors.toList())            .collect(Collectors.toSet())            .collect(Collectors.joining(", ", "[", "]"))
.collect(Collectors.toMap(Person::id, Person::name))                              // duplicate keys -> IllegalStateException, add a merge fn
.collect(Collectors.groupingBy(Order::city))                                      // Map<String, List<Order>>
.collect(Collectors.groupingBy(Order::city, Collectors.counting()))               // Map<String, Long>
.collect(Collectors.groupingBy(Order::city, Collectors.summingDouble(Order::total)))
.collect(Collectors.groupingBy(Order::city, Collectors.averagingDouble(Order::total)))
.collect(Collectors.groupingBy(Order::city, TreeMap::new, Collectors.counting())) // sorted keys
.collect(Collectors.groupingBy(Order::city, Collectors.mapping(Order::id, Collectors.toList())))
.collect(Collectors.partitioningBy(o -> o.total() > 500))                         // Map<Boolean, List<Order>>
.collect(Collectors.summarizingDouble(Order::total))                              // count, sum, min, avg, max in one go
```
### Recipes
```java
// total revenue per city, highest first
sales.stream().collect(groupingBy(Sale::city, summingDouble(Sale::amount)))
     .entrySet().stream().sorted(Map.Entry.<String, Double>comparingByValue().reversed())
     .limit(3).forEach(e -> System.out.printf("%-10s %,.2f%n", e.getKey(), e.getValue()));
// unique sorted names
people.stream().map(Person::name).distinct().sorted().toList();
// average of a list of Integers
nums.stream().mapToInt(Integer::intValue).average().orElse(0);
// text bar chart
counts.forEach((k, v) -> System.out.println(k + " " + "#".repeat(v)));
```

## Optional (a value that may be missing)
```java
Optional<String> first = names.stream().filter(n -> n.startsWith("A")).findFirst();
first.isPresent()  first.orElse("none")  first.orElseThrow()  first.map(String::toUpperCase)  first.ifPresent(System.out::println)
Optional.of(x) /* x not null */   Optional.ofNullable(x)   Optional.empty()
```

## Gotchas
| Trap | Fix |
|---|---|
| `List.of(...)`, `Map.of(...)`, `stream.toList()` are **immutable** → `UnsupportedOperationException` | wrap: `new ArrayList<>(List.of(...))` |
| `map.get(missing)` returns `null` → NPE when unboxed | `getOrDefault` / `merge` |
| `list.remove(int)` vs `list.remove(Object)` on `List<Integer>` | `list.remove(Integer.valueOf(5))` |
| `==` between `Integer` objects works only for −128…127 | use `.equals` |
| Modifying a list while looping over it | `removeIf`, or an `Iterator`, or loop over a copy |
| `HashMap` / `HashSet` order is not guaranteed | `LinkedHash…` or `Tree…` when order matters |
| Custom class as key/in a set needs `equals` **and** `hashCode` | use a `record` (done for you) |
| Reusing a consumed stream → `IllegalStateException` | create a new stream |
