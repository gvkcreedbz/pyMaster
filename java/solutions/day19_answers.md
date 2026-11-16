# Day 19 - Quiz answers
1. A class is the blueprint (it says which fields and methods exist). An object is one real thing built from it with `new`. One class can make many objects, each with its own data.
2. `this` is the object the method is working on. You need `this.name = name;` in a constructor (or setter) when the parameter has the same name as the field: plain `name` means the parameter, `this.name` means the field.
3. It runs once, when you create the object with `new`. It has the same name as the class and no return type (not even `void`).
4. Unreadable text made of the class name and a number, like `Rectangle@1b6d3586`. Write `toString()` to control it.
5. A `static` field exists once for the whole class and is shared by all objects (a counter, a constant like `BANK_NAME`). An instance field exists once per object, with its own value.
6. So that outside code can only change the data through your methods, and your methods can enforce the rules (no negative balance, no temperature below absolute zero).
7. It hands out the real internal list, so a caller can add or clear entries and break the account. Return a copy (`new ArrayList<>(history)`) or an unmodifiable list.
8. `hashCode()`. Equal objects must have equal hash codes, otherwise `HashSet` and `HashMap` (which use the hash first) treat equal objects as different and store duplicates.
