# Day 15 - Quiz answers

1. It overwrites the file: the old content is erased and replaced (and the file is created if it did not exist).
2. Use the append option: `Files.writeString(path, text + "\n", StandardOpenOption.CREATE, StandardOpenOption.APPEND)` (or `Files.write(path, lines, StandardOpenOption.APPEND)`).
3. A list of two items: `["x", "y"]`. The line endings are removed.
4. The method might fail with an input/output problem (missing file, full disk). Java makes callers either declare the same `throws` or handle the error (Day 17).
5. `c.txt` - the last part of the path.
6. They add the correct separator for the operating system (`/` or `\`), so the program works on Windows, Mac and Linux.
7. The stream keeps the folder open; `try (...)` closes it automatically, even if something goes wrong.
8. Characters like `₹` or emojis only survive if the program writes and reads with the same encoding; UTF-8 everywhere is the safe choice.
