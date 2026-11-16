# Day 13 - Quiz answers

1. `r.city()` - record getters have the field's name, no `get` prefix.
2. A constructor, the getter methods, `equals`/`hashCode` and a readable `toString` (`Restaurant[name=..., city=...]`). The fields cannot change afterwards.
3. `restaurants.get(0).cuisines().get(1)` (list position, then field, then list position).
4. It never crashes: if the key is missing you get the default value instead of `null` (which would cause a `NullPointerException` on the next step).
5. If `city` has no list in the map yet, it creates an empty `ArrayList` and stores it; either way it returns the list for that city, so you can `.add(...)` straight away.
6. `[1,"a"]` (numbers plain, text in double quotes, no spaces).
7. `Map.of` (and `List.of`) do not allow `null` keys or values; they throw a `NullPointerException`. Use a `HashMap` and `put(key, null)`.
8. No, it is a shallow copy: you get a new list, but the items inside are the *same* objects. That is safe for strings and records because they never change.
