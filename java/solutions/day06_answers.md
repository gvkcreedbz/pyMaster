# Day 06 - Quiz answers

1. `for (int i = 2; i < 10; i += 3)` gives `2, 5, 8` (start at 2, step 3, stop before 10).
2. `0`, `1`, `2`, each on its own line (`for (int i = 0; i < 3; i++) System.out.println(i);`).
3. Zero times: the condition `5 < 3` is false from the start, so the body is skipped. (A `do { } while (...)` loop would run its body once.)
4. `break` leaves the whole loop immediately. `continue` skips the rest of the current round and jumps to the next round.
5. `6`. (`int total = 0; for (int n : new int[]{1, 2, 3}) total += n;`: 0 + 1 + 2 + 3.)
6. Press **Ctrl + C** in the terminal (or the red stop button in the editor).
7. `for (int i = 5; i >= 1; i--) { System.out.println(i); }`
8. `count` never changes, so `count < 3` stays true forever: an infinite loop printing `0`. Add `count++;` inside the loop.
