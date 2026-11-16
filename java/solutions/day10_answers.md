# Day 10 - Quiz answers

1. `d.get("b")` gives `null` (no such key). `d.getOrDefault("b", 0)` gives `0`.
2. `d.containsKey("b")`. (`containsValue(x)` checks the values.)
3. It **replaces** the old value with `5`. A map keeps only one value per key.
4. `counts.merge(word, 1, Integer::sum);` (or `counts.put(word, counts.getOrDefault(word, 0) + 1);`).
5. `TreeMap` keeps the keys sorted; `LinkedHashMap` keeps the insertion order. (`HashMap` promises no order.)
6. `for (Map.Entry<String, Integer> e : d.entrySet()) { ... e.getKey() ... e.getValue() ... }`
7. Generic types such as `Map` can only hold objects. `int` is a primitive type, so use its wrapper `Integer`.
8. `List.sort` is stable: items with an equal count keep their earlier relative order. If the list was A-Z before the sort by count, equal-count words stay A-Z.
