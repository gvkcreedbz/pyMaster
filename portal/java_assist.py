"""Java code-coaching helpers for the offline tutor (twin of the Python helpers in `assistant.py`).

Pure functions, standard library only (no AST library, no JDK needed):

    decode_error(text)   -> str | None        friendly explanation of javac / JVM messages   (assistant._decode_error)
    static_review(code)  -> list[str]         heuristic coach tips for Java source (max 5)    (assistant.static_review)
    looks_code(text)     -> bool              does this text look like Java (or SQL)?         (assistant._looks_code)
    concept_keywords()   -> dict[str, list]   {kb_java entry id: [keywords]}                  (find_concepts' keyword table)

Extras the integrator may want: looks_like_error(text), find_concepts(...), day_concepts(...) (same algorithms as
assistant.py but over `kb_java.KB`).
"""
from __future__ import annotations

import re

try:                                        # normal use: portal.java_assist
    from . import kb_java
except ImportError:                         # run as a top-level module
    import kb_java                          # type: ignore

# =====================================================================================================
# decode_error
# =====================================================================================================
_IMPORTS = {
    "Scanner": "java.util.Scanner", "List": "java.util.List", "ArrayList": "java.util.ArrayList", "Map": "java.util.Map",
    "HashMap": "java.util.HashMap", "TreeMap": "java.util.TreeMap", "LinkedHashMap": "java.util.LinkedHashMap",
    "Set": "java.util.Set", "HashSet": "java.util.HashSet", "TreeSet": "java.util.TreeSet", "Arrays": "java.util.Arrays",
    "Collections": "java.util.Collections", "Random": "java.util.Random", "Optional": "java.util.Optional",
    "Collectors": "java.util.stream.Collectors", "Stream": "java.util.stream.Stream", "IntStream": "java.util.stream.IntStream",
    "Files": "java.nio.file.Files", "Path": "java.nio.file.Path", "Paths": "java.nio.file.Paths",
    "IOException": "java.io.IOException", "File": "java.io.File", "Pattern": "java.util.regex.Pattern",
    "Matcher": "java.util.regex.Matcher", "LocalDate": "java.time.LocalDate", "LocalDateTime": "java.time.LocalDateTime",
    "Duration": "java.time.Duration", "HttpClient": "java.net.http.HttpClient", "BigDecimal": "java.math.BigDecimal",
    "Function": "java.util.function.Function", "Predicate": "java.util.function.Predicate",
    "Logger": "java.util.logging.Logger", "Level": "java.util.logging.Level",
}


def _b(title: str, meaning: str, fix: str) -> str:
    """One bullet in the same shape as assistant._decode_error: - `Error`: **meaning**. Typical fix: ..."""
    return f"- `{title}`: **{meaning}**. Typical fix: {fix}"


def _cut(s: str, n: int = 60) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _tail(m, text: str, n: int = 500) -> str:
    return text[m.end(): m.end() + n]


# ---- compile errors (javac) -------------------------------------------------------------------------
def _r_symbol(m, text):
    sm = re.search(r"symbol:\s*(variable|method|class)\s+([^\s(]+)", _tail(m, text, 400))
    kind, name = (sm.group(1), sm.group(2)) if sm else ("", "")
    if kind == "class":
        imp = _IMPORTS.get(name)
        if imp:
            return _b("cannot find symbol", f"Java doesn't know the class `{name}` here",
                      f"add `import {imp};` at the top (check the capital letters too).")
        return _b("cannot find symbol", f"Java doesn't know a class called `{name}`",
                  "check spelling and capitals (`String`, not `string`), add the missing `import`, or create the class/file.")
    if kind == "variable":
        return _b("cannot find symbol", f"the variable `{name}` doesn't exist at this point",
                  "typo or wrong capitals? Declared with a type (`int total = 0;`)? Declared *inside* another `{ }` block, so it is out of scope here? "
                  "Text needs quotes (`\"hello\"`).")
    if kind == "method":
        extra = ""
        if name in ("length", "size", "length()"):
            extra = " Remember: arrays use `.length` (no parentheses), `String` uses `.length()`, lists use `.size()`."
        return _b("cannot find symbol", f"there is no method `{name}` that fits here",
                  "check the spelling, the capitals (`toUpperCase`), the arguments, and that the *type* really has that method." + extra)
    return _b("cannot find symbol", "javac has never heard of that name in this place",
              "read the `symbol:` line under the error: it names the variable, method or class. Usually a typo, a missing `import`, or a variable declared in another block.")


def _r_semicolon(m, text):
    return _b("';' expected", "a statement isn't finished: the `;` is missing at the end of the line javac points to (or one above it)",
              "add `;` after the statement. Every statement ends with `;` but `if (...) {` and `for (...) {` headers do not.")


def _r_expected(m, text):
    tok = m.group(1)
    return _b(f"'{tok}' expected", f"javac needed a `{tok}` here and found something else",
              "count your brackets: every `(` needs `)`, every `[` needs `]`, every `{` needs `}`. A missing one is often on the line *above*.")


def _r_identifier(m, text):
    return _b("<identifier> expected", "javac expected a name (of a variable, method or class) but found something else",
              "statements such as `System.out.println(...)` must be *inside* a method, not directly in the class body; also check for a stray `;` or `(`.")


def _r_illegal_start(m, text):
    return _b(m.group(0), "javac can't make sense of the code here, usually a bracket problem just before",
              "look at the line above for a missing `)` or `;`, or a method written inside another method (methods can't be nested).")


def _r_not_stmt(m, text):
    return _b("not a statement", "that line is an expression that does nothing on its own (like `x + 1;` or `\"hi\";`)",
              "assign the result (`x = x + 1;`), call something (`System.out.println(x);`), or remove the line. Often `=` was meant instead of `==`/`+`.")


def _r_eof(m, text):
    return _b("reached end of file while parsing", "a `{` was opened but never closed",
              "count your braces from the top; indent consistently (IDE: Format Document) so the unmatched `{` stands out.")


def _r_class_expected(m, text):
    return _b("class, interface, enum, or record expected", "code was found outside any class, usually after one `}` too many",
              "remove the extra `}` (compare indentation), and put methods inside a class.")


def _r_else(m, text):
    return _b("'else' without 'if'", "an `else` doesn't have a matching `if` right before it",
              "check for a stray `;` after the `if (...)`, or an `if` body without braces where you added a second line.")


def _r_lossy(m, text):
    a, b = m.group(1), m.group(2)
    return _b(f"incompatible types: possible lossy conversion from {a} to {b}", f"you're squeezing a `{a}` into a smaller `{b}` and would lose information",
              f"if you really want that, cast it: `({b}) value`; or declare the variable as `{a}`. Note `int x = 5 / 2.0;` is a `double` expression.")


def _r_incompat(m, text):
    a, b = _cut(m.group(1), 30), _cut(m.group(2), 30)
    return _b("incompatible types", f"a `{a}` was given where a `{b}` is needed",
              "convert it on purpose: `Integer.parseInt(text)`, `String.valueOf(n)`, `Double.parseDouble(s)`; or fix the variable's declared type.")


def _r_unexpected_return(m, text):
    return _b("incompatible types: unexpected return value", "you wrote `return value;` inside a `void` method",
              "either make the return type real (`int`, `String`...) or `return;` with nothing.")


def _r_missing_return(m, text):
    return _b("missing return statement", "some path through the method ends without returning a value",
              "make every path `return` (add a final `return` after the `if`/`for`, or an `else`). `void` methods don't need one.")


def _r_public_file(m, text):
    n = m.group(1)
    return _b(f"class {n} is public, should be declared in a file named {n}.java", f"a `public class {n}` must live in a file called exactly `{n}.java`",
              f"rename the file to `{n}.java` (capitals count), or remove `public` from the class.")


def _r_unclosed_str(m, text):
    return _b("unclosed string literal", "a `\"` was opened but not closed on the same line",
              "add the closing `\"`. Strings can't span lines (use a text block `\"\"\"` or join with `+`).")


def _r_unclosed_char(m, text):
    return _b("unclosed character literal", "a `'` opened a `char` that isn't closed (or you used single quotes for text)",
              "`'a'` holds exactly one character; for several characters use double quotes: `\"abc\"`.")


def _r_unclosed_comment(m, text):
    return _b("unclosed comment", "a `/*` comment was never closed", "add `*/` where the comment should end.")


def _r_static_ctx(m, text):
    kind, name = m.group(1), m.group(2).split("(")[0]
    call = f"{name}(...)" if kind == "method" else name
    return _b("non-static ... cannot be referenced from a static context", f"`main` is `static`, but `{name}` belongs to an object (it isn't `static`)",
              f"make `{name}` `static`, or create an object first (`new MyClass().{call}`) and use it through that object.")


def _r_uninit(m, text):
    n = m.group(1)
    return _b("variable might not have been initialized", f"`{n}` is read before every path has given it a value",
              f"give it a starting value (`int {n} = 0;`) or make sure each `if`/`else`/`switch` branch assigns it.")


def _r_unreported(m, text):
    ex = m.group(1)
    return _b(f"unreported exception {ex}", f"this call can throw the *checked* exception `{ex}` and you neither caught nor declared it",
              f"wrap the call in `try {{ ... }} catch ({ex} e) {{ ... }}`, or add `throws {ex}` to the method header.")


def _r_cannot_apply(m, text):
    return _b("cannot be applied to given types", "you called a method/constructor with the wrong number or types of arguments",
              "read the `required:` and `found:` lines under the error: they list what it wants and what you gave.")


def _r_no_suitable(m, text):
    return _b("no suitable method/constructor found", "none of the overloads accepts the arguments you passed",
              "compare your arguments with the `method ... is not applicable` lines javac prints; check order and types.")


def _r_already_defined(m, text):
    n = m.group(1)
    return _b("variable is already defined", f"`{n}` was declared twice in the same scope",
              f"remove the type on the second use (`{n} = ...;` instead of `int {n} = ...;`), or give the second variable another name.")


def _r_final_assign(m, text):
    n = m.group(1)
    return _b("cannot assign a value to final variable", f"`{n}` is `final`, so it can be set only once",
              "remove `final` if it must change, or compute the final value in one go.")


def _r_bad_operand(m, text):
    op = m.group(1)
    return _b(f"bad operand types for binary operator '{op}'", f"the two values on either side of `{op}` aren't compatible types",
              "compare like with like: `String`s with `.equals(...)`, numbers with numbers; convert text with `Integer.parseInt`.")


def _r_unreachable(m, text):
    return _b("unreachable statement", "the code after a `return`, `break`, `continue`, `throw` or an endless loop can never run",
              "delete it, or move it before the jump.")


def _r_pkg_missing(m, text):
    return _b(f"package {m.group(1)} does not exist", "the package in the `import` isn't on the classpath (or is misspelled)",
              "fix the spelling, or add the library to `pom.xml` / `build.gradle`. For JDK classes check the exact package name.")


def _r_deref(m, text):
    t = m.group(1)
    return _b(f"{t} cannot be dereferenced", f"you used `.` on a primitive `{t}`; primitives have no methods",
              "use the wrapper (`Integer.valueOf(x)`), `String.valueOf(x)`, or a static helper (`Integer.toString(x)`).")


def _r_array_req(m, text):
    return _b("array required, but X found", "you used `[index]` on something that isn't an array",
              "for `String` use `.charAt(i)`, for `List` use `.get(i)`, for `Map` use `.get(key)`.")


def _r_private(m, text):
    return _b("has private access", f"`{m.group(1)}` is `private` in another class",
              "use a public getter/method of that class, or make the member package-private/public if that's the design.")


def _r_abstract(m, text):
    return _b("is not abstract and does not override abstract method", f"your class promised to implement `{m.group(1)}` but didn't",
              "add that method (same name, parameters and return type, marked `@Override`), or declare the class `abstract`.")


def _r_main_missing(m, text):
    return _b("Could not find or load main class / Main method not found", "`java` can't find a class (or a correct `main`) to start",
              "the signature must be exactly `public static void main(String[] args)`; run from the folder containing the `.class`, "
              "and use the class name without `.java`/`.class`.")


def _r_invalid_method(m, text):
    return _b("invalid method declaration; return type required", "a method header has no return type (or the constructor name doesn't match the class)",
              "write the return type (`void`, `int`...); a constructor must have exactly the class's name, with capitals.")


def _r_class_version(m, text):
    return _b("UnsupportedClassVersionError", "the class was compiled with a newer JDK than the one running it",
              "run with the same (or a newer) JDK: check `java -version` and `javac -version` match.")


# ---- runtime errors (JVM) ---------------------------------------------------------------------------
def _r_npe(m, text):
    hint = re.search(r"Cannot ([^\n]*?) because ([^\n]*?) is null", text)
    if hint:
        what, who = hint.group(1), hint.group(2)
        if "return value of" in who:
            cause = (f"the method call {who.replace('the return value of ', '')} gave back `null` (a `Map.get` for a missing key is the classic) "
                     "and then the code used it")
            fix = "use `getOrDefault`, `containsKey`, or check `!= null`/`Optional` before using the result."
        else:
            cause = f"{who} is `null`, and the code tried to {what}"
            fix = ("find where that variable should have been given a value (a missing `new`, a failed lookup, a method that returned `null`); "
                   "add a check or initialise it.")
            if "<local" in who:
                fix += " (Names like `<local4>` appear when the class is compiled without `-g`; compile with `javac -g` to see real names.)"
        return _b("NullPointerException", f"Java 21's helpful message says {cause}", fix)
    return _b("NullPointerException", "you used a variable that points at nothing (`null`) as if it were an object",
              "find which variable is `null` on the failing line (the `at ...(File.java:N)` line tells you the line); initialise it with `new`, "
              "or check `if (x != null)`. Comparing strings? Write `\"abc\".equals(x)`.")


def _idx_nums(m, text):
    t = text[m.start(): m.end() + 200]
    a = re.search(r"[Ii]ndex (-?\d+) out of bounds for length (\d+)", t) or re.search(r"index (-?\d+),? length (\d+)", t)
    return (int(a.group(1)), int(a.group(2))) if a else None


def _r_aioobe(m, text):
    n = _idx_nums(m, text)
    if n:
        i, ln = n
        detail = (f"you asked for index {i} but the array only has {ln} element{'s' if ln != 1 else ''} (valid positions are 0 to {ln - 1})"
                  if ln else f"you asked for index {i} but the array/list is empty")
    else:
        detail = "you used an index that doesn't exist in the array or list"
    return _b("ArrayIndexOutOfBoundsException / IndexOutOfBoundsException", detail,
              "indexes run `0 … length-1`; loops should use `i < arr.length` (not `<=`); lists use `size()`; an empty list has no index 0.")


def _r_sioobe(m, text):
    t = _tail(m, text, 200)
    a = re.search(r"begin (-?\d+), end (-?\d+), length (\d+)", t)
    if a:
        b, e, ln = a.groups()
        detail = f"`substring({b}, {e})` was called on a String of length {ln}; the end must be at most {ln} and the start at most the end"
    else:
        n = _idx_nums(m, text)
        detail = (f"`charAt({n[0]})` was called on a String of length {n[1]}; valid positions are 0 to {max(n[1] - 1, 0)}" if n
                  else "you asked for a character position that isn't inside the String")
    return _b("StringIndexOutOfBoundsException", detail,
              "check `s.length()` first (`s.isEmpty()` for empty text); `substring(start, end)` excludes `end`; the last char is at `length() - 1`.")


def _r_arith(m, text):
    if re.search(r"Non-terminating decimal expansion", text):
        return _b("ArithmeticException: Non-terminating decimal expansion", "a `BigDecimal` division has no exact answer (like 1/3)",
                  "give a scale and rounding: `a.divide(b, 2, RoundingMode.HALF_UP)`.")
    return _b("ArithmeticException: / by zero", "an `int`/`long` was divided (or `%`) by zero",
              "check the divisor first (`if (count == 0) ...`). `double` division by zero gives `Infinity` instead of an error, so the bug can hide.")


def _r_cce(m, text):
    a = re.search(r"class (\S+) cannot be cast to class (\S+)", _tail(m, text, 300))
    if a:
        src, dst = a.group(1).rsplit(".", 1)[-1], a.group(2).rsplit(".", 1)[-1].rstrip(",")
        detail = f"an object of type `{src}` was cast to `{dst}`, but it isn't one"
    else:
        detail = "you cast an object to a type it isn't"
    return _b("ClassCastException", detail,
              "avoid the cast with generics (`List<String>` instead of a raw `List`); if you must, test first: `if (o instanceof Dog d) { ... }`.")


def _r_nfe(m, text):
    a = re.search(r'For input string: "(.*?)"', _tail(m, text, 300))
    if a:
        s = a.group(1)
        detail = (f"`parseInt/parseDouble` was given `\"{s}\"`, which isn't a valid number" if s.strip() else
                  "`parseInt/parseDouble` was given an empty (or blank) string")
    elif re.search(r"Cannot parse null string|:\s*null\b", _tail(m, text, 80)):
        detail = "`parseInt/parseDouble` was given `null`"
    elif re.search(r"empty String", _tail(m, text, 80)):
        detail = "`parseDouble` was given an empty string"
    else:
        detail = "text that isn't a valid number was converted to a number"
    return _b("NumberFormatException", detail,
              "`trim()` the text, validate it first (`s.matches(\"-?\\\\d+\")`), or catch `NumberFormatException` and ask again. `parseInt(\"3.7\")` fails: use `parseDouble`.")


def _r_inputmismatch(m, text):
    return _b("InputMismatchException", "`Scanner.nextInt()` / `nextDouble()` found text that isn't that kind of number (the bad token is left unread)",
              "read a line and parse it (`Integer.parseInt(in.nextLine().trim())`) inside try/catch, or call `in.next()` / `in.nextLine()` to throw the bad token away before retrying.")


def _r_nosuchelement(m, text):
    t = _tail(m, text, 120) + text[max(0, m.start() - 10): m.end() + 40]
    if "No line found" in t:
        d, f = ("`Scanner.nextLine()` was called but there is no more input (the user pressed Ctrl+Z/Ctrl+D, input ran out, or a previous read used the last line)",
                "check `in.hasNextLine()` first; in tests make sure the fed input contains every line the program reads.")
    elif "No value present" in t:
        d, f = ("`Optional.get()` / `orElseThrow()` was called on an empty Optional",
                "use `orElse(default)`, `ifPresent(...)`, or check `isPresent()` first.")
    else:
        d, f = ("`next()`/`nextInt()`/`iterator.next()` was called when nothing is left",
                "guard with `hasNext()`/`hasNextInt()`/`!list.isEmpty()` before reading.")
    return _b("NoSuchElementException", d, f)


def _r_cme(m, text):
    return _b("ConcurrentModificationException", "a collection was changed (add/remove) while a loop was walking over it",
              "use `list.removeIf(...)`, an explicit `Iterator` with `it.remove()`, or collect the changes and apply them after the loop.")


def _r_so(m, text):
    return _b("StackOverflowError", "a method keeps calling itself (or two methods call each other) so deeply that the call stack ran out",
              "make sure every recursive call moves toward a **base case** that returns without recursing; for very deep work use a loop.")


def _r_oom(m, text):
    t = _tail(m, text, 80)
    if "unable to create native thread" in t:
        d, f = ("the program started far too many threads", "use a thread pool (`Executors.newFixedThreadPool`) or virtual threads instead of one thread per task.")
    elif "Metaspace" in t:
        d, f = ("the JVM ran out of memory for class definitions", "look for code that generates classes endlessly, or raise `-XX:MaxMetaspaceSize`.")
    else:
        d, f = ("the program needs more memory than the JVM heap allows",
                "stop keeping everything in memory (stream files with `Files.lines`, process in batches, don't grow a static list forever); "
                "only as a last step raise `-Xmx`.")
    return _b("OutOfMemoryError", d, f)


def _r_unsupported_op(m, text):
    return _b("UnsupportedOperationException", "you tried to change a read-only collection (`List.of`, `Map.of`, `stream.toList()`, `Arrays.asList` size changes)",
              "copy it first: `new ArrayList<>(List.of(...))`.")


def _r_illegal_arg(m, text):
    return _b("IllegalArgumentException", "a method refused the value you gave it (the message after the colon says why)",
              "read the message; check the value against the method's documented rules (range, null, format).")


def _r_illegal_state(m, text):
    return _b("IllegalStateException", "a method was called at the wrong time for the object's current state",
              "check the order of calls (for example: using a closed resource, or `iterator.remove()` before `next()`).")


def _r_filenotfound(m, text):
    a = re.search(r"(?:NoSuchFileException|FileNotFoundException):\s*([^\n(]+)", text)
    p = a.group(1).strip() if a else ""
    where = f" `{_cut(p, 50)}`" if p else ""
    return _b("FileNotFoundException / NoSuchFileException", f"Java couldn't find the file{where} from the program's *working directory*",
              "print `Path.of(\"\").toAbsolutePath()` to see where it looks; use the correct relative path (`../../datasets/sales.csv`) or an absolute one.")


def _r_negative_size(m, text):
    return _b("NegativeArraySizeException", "an array was created with a negative length", "check the size variable before `new int[n]` (it should be 0 or more).")


def _r_classnotfound(m, text):
    return _b("ClassNotFoundException / NoClassDefFoundError", "the JVM can't find a class at run time (often a library missing from the classpath)",
              "add the jar to `-cp` (or the dependency to `pom.xml`/`build.gradle`); check package names and that the `.class` file exists.")


def _r_sql(m, text):
    t = text
    if "No suitable driver" in t:
        return _b("SQLException: No suitable driver", "no JDBC driver jar is on the classpath for that `jdbc:` URL",
                  "add the driver (for SQLite: `sqlite-jdbc`) to the classpath / dependencies, and check the URL starts `jdbc:sqlite:`.")
    a = re.search(r"no such table:\s*(\w+)", t)
    if a:
        return _b("SQLException: no such table", f"the table `{a.group(1)}` doesn't exist in *this* database file",
                  "run the `CREATE TABLE` first, and check the database path (a relative path creates a new empty file in the working directory).")
    return _b("SQLException", "the database rejected the SQL or the connection",
              "read the message after the colon: wrong table/column names, missing `?` values (JDBC indexes start at 1), or a closed connection.")


def _r_datetime(m, text):
    return _b("DateTimeParseException", "text didn't match the date/time pattern you asked for",
              "check the pattern letters (`yyyy-MM-dd`, `MM` = month, `mm` = minutes) and that the text really has that shape.")


# (key, regex, handler) in priority order; hits are reported in order of appearance in the text
_RULES: list[tuple[str, re.Pattern, object]] = [(k, re.compile(rx), fn) for k, rx, fn in [
    # --- compile time ---
    ("symbol", r"cannot find symbol", _r_symbol),
    ("expected", r"';' expected", _r_semicolon),
    ("identifier", r"<identifier> expected", _r_identifier),
    ("expected", r"'([)\]}(\[,.])'(?: or '[^']+')* expected", _r_expected),
    ("illegal_start", r"illegal start of (?:expression|type)", _r_illegal_start),
    ("not_stmt", r"\bnot a statement", _r_not_stmt),
    ("eof", r"reached end of file while parsing", _r_eof),
    ("class_expected", r"class, interface, enum, or record expected", _r_class_expected),
    ("else", r"'else' without 'if'", _r_else),
    ("lossy", r"possible lossy conversion from (\w+) to (\w+)", _r_lossy),
    ("unexpected_return", r"incompatible types: unexpected return value", _r_unexpected_return),
    ("incompat", r"incompatible types: (?!possible lossy|unexpected return)(.+?) cannot be converted to ([\w.<>\[\]?, ]+)", _r_incompat),
    ("missing_return", r"missing return statement", _r_missing_return),
    ("public_file", r"class (\w+) is public, should be declared in a file named", _r_public_file),
    ("unclosed_str", r"unclosed string literal", _r_unclosed_str),
    ("unclosed_char", r"unclosed character literal", _r_unclosed_char),
    ("unclosed_comment", r"unclosed comment", _r_unclosed_comment),
    ("static_ctx", r"non-static (variable|method) ([\w()]+?) cannot be referenced from a static context", _r_static_ctx),
    ("uninit", r"variable (\w+) might not have been initialized", _r_uninit),
    ("unreported", r"unreported exception ([\w.]+)", _r_unreported),
    ("cannot_apply", r"(?:method|constructor) [\w<>]+ in (?:class|record|enum|interface) [\w<>]+ cannot be applied to given types", _r_cannot_apply),
    ("no_suitable", r"no suitable (?:method|constructor) found", _r_no_suitable),
    ("already_defined", r"variable (\w+) is already defined in", _r_already_defined),
    ("final_assign", r"cannot assign a value to final variable (\w+)", _r_final_assign),
    ("bad_operand", r"bad operand types? for (?:binary|unary) operator '([^']+)'", _r_bad_operand),
    ("unreachable", r"unreachable statement", _r_unreachable),
    ("pkg_missing", r"package ([\w.]+) does not exist", _r_pkg_missing),
    ("deref", r"(\w+) cannot be dereferenced", _r_deref),
    ("array_req", r"array required, but \S+ found", _r_array_req),
    ("private", r"(\S+) has private access in", _r_private),
    ("abstract", r"is not abstract and does not override abstract method (\S+) in", _r_abstract),
    ("invalid_method", r"invalid method declaration; return type required", _r_invalid_method),
    ("class_version", r"UnsupportedClassVersionError|compiled by a more recent version of the Java Runtime", _r_class_version),
    ("main_missing", r"Could not find or load main class|Main method not found in class|Error: Main method is not static", _r_main_missing),
    # --- run time ---
    ("npe", r"NullPointerException", _r_npe),
    ("index", r"ArrayIndexOutOfBoundsException", _r_aioobe),
    ("index", r"(?<![A-Za-z])IndexOutOfBoundsException", _r_aioobe),
    ("index", r"StringIndexOutOfBoundsException", _r_sioobe),
    ("index", r"(?<!\w)Index -?\d+ out of bounds for length \d+", _r_aioobe),
    ("arith", r"ArithmeticException|/ by zero|BigInteger divide by zero", _r_arith),
    ("cce", r"ClassCastException", _r_cce),
    ("nfe", r"NumberFormatException", _r_nfe),
    ("mismatch", r"InputMismatchException", _r_inputmismatch),
    ("nosuch", r"NoSuchElementException", _r_nosuchelement),
    ("cme", r"ConcurrentModificationException", _r_cme),
    ("so", r"StackOverflowError", _r_so),
    ("oom", r"OutOfMemoryError", _r_oom),
    ("unsupported", r"UnsupportedOperationException", _r_unsupported_op),
    ("negsize", r"NegativeArraySizeException", _r_negative_size),
    ("illegal_arg", r"(?<![A-Za-z])IllegalArgumentException", _r_illegal_arg),
    ("illegal_state", r"IllegalStateException", _r_illegal_state),
    ("filenotfound", r"(?<!unreported exception )(?:FileNotFoundException|NoSuchFileException)", _r_filenotfound),
    ("classnotfound", r"ClassNotFoundException|NoClassDefFoundError", _r_classnotfound),
    ("sql", r"(?<!unreported exception )(?:SQLException|No suitable driver|no such table)", _r_sql),
    ("datetime", r"DateTimeParseException", _r_datetime),
]]

_ANY_EXC = re.compile(r"\b(?:[a-z_]\w*\.)*([A-Z]\w*(?:Exception|Error))\b")
_COMPILE_LOC = re.compile(r"([\w$./\\:-]*?[\w$-]+\.java):(\d+):\s*(?:error|warning)")
_FRAME = re.compile(r"^\s*at\s+(?!(?:java|jdk|javax|sun|org\.junit|org\.apache|org\.springframework)\.)[\w$.<>/]+\(([\w$-]+\.java):(\d+)\)", re.M)


def _location(text: str, pos: int, compile_time: bool) -> str:
    if compile_time:
        found = None
        for lm in _COMPILE_LOC.finditer(text):
            if lm.start() <= pos:
                found = lm
        if found:
            fname = re.split(r"[\\/]", found.group(1))[-1]
            return f" *({fname}, line {found.group(2)})*"
        return ""
    fm = _FRAME.search(text, pos) or _FRAME.search(text)
    return f" *(first frame in your code: {fm.group(1)}, line {fm.group(2)})*" if fm else ""


_COMPILE_KEYS = {"symbol", "expected", "identifier", "illegal_start", "not_stmt", "eof", "class_expected", "else", "lossy", "unexpected_return",
                 "incompat", "missing_return", "public_file", "unclosed_str", "unclosed_char", "unclosed_comment", "static_ctx", "uninit",
                 "unreported", "cannot_apply", "no_suitable", "already_defined", "final_assign", "bad_operand", "unreachable", "pkg_missing",
                 "deref", "array_req", "private", "abstract", "invalid_method"}


def decode_error(text: str) -> str | None:
    """Friendly explanation of javac / JVM messages found in `text`; None if nothing recognisable.

    Returns up to two bullets (same shape as assistant._decode_error): "- `Error`: **meaning**. Typical fix: ...".
    """
    if not text or not text.strip():
        return None
    hits = []
    for order, (key, rx, fn) in enumerate(_RULES):
        m = rx.search(text)
        if m:
            hits.append((m.start(), order, key, fn, m))
    out: list[str] = []
    if hits:
        hits.sort(key=lambda h: (h[0], h[1]))
        seen: set[str] = set()
        for pos, _, key, fn, m in hits:
            if key in seen:
                continue
            seen.add(key)
            out.append(fn(m, text) + _location(text, pos, key in _COMPILE_KEYS))
            if len(out) == 2:
                break
        return "\n".join(out)
    am = _ANY_EXC.search(text)
    if am:
        return (f"`{am.group(1)}`: read the **first line** of the stack trace (type and message), then the first `at ...(File.java:N)` line that "
                "names *your own* class; that is where to look.")
    return None


def looks_like_error(text: str) -> bool:
    """True when the text looks like javac output or a JVM stack trace (use for the 'debug' intent)."""
    if not text:
        return False
    return bool(re.search(r"\.java:\d+:\s*error|\berror:\s|Exception in thread|\bCaused by:|\b[A-Z]\w*(?:Exception|Error)\b|"
                          r"^\s+at [\w$.]+\([\w$]+\.java:\d+\)", text, re.M))


# =====================================================================================================
# static_review
# =====================================================================================================
_CONTROL = {"if", "for", "while", "switch", "catch", "synchronized", "try", "else", "do", "return", "super", "this", "assert"}
_HDR = re.compile(r"^(?:@\w+(?:\([^)]*\))?\s*)*(?:[\w<>\[\],.?&\s]*?\s)?(\w+)\s*\(([^()]*)\)\s*(?:throws\s+[\w.,\s]+)?$", re.S)
_PRIMS_OK = {"0", "1", "2", "10", "100", "1000"}
_RAW = ("List|ArrayList|LinkedList|Map|HashMap|TreeMap|LinkedHashMap|Set|HashSet|TreeSet|LinkedHashSet|Optional|Iterator|"
        "Comparable|Collection|Queue|Deque|ArrayDeque|PriorityQueue|Comparator")


def _blank(s: str) -> str:
    return re.sub(r"[^\n]", " ", s)


def _mask(code: str) -> str:
    """Same length and line structure as `code`, with comments and the insides of string/char literals blanked out."""
    out: list[str] = []
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        two = code[i:i + 2]
        if two == "//":
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif two == "/*":
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(_blank(code[i:j]))
            i = j
        elif code.startswith('"""', i):
            j = code.find('"""', i + 3)
            j = n if j < 0 else j + 3
            seg = code[i:j]
            out.append('"' + _blank(seg[1:-1]) + '"' if len(seg) >= 2 else seg)
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and code[j] not in (c, "\n"):
                j += 2 if code[j] == "\\" else 1
            if j < n and code[j] == c:
                out.append(c + _blank(code[i + 1:j]) + c)
                i = j + 1
            else:
                j = min(j, n)
                out.append(c + _blank(code[i + 1:j]))
                i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _line(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _pairs(masked: str) -> tuple[dict[int, int], str | None]:
    """Matching bracket positions plus a human message if the brackets don't balance."""
    stack: list[tuple[str, int]] = []
    pairs: dict[int, int] = {}
    closers = {")": "(", "}": "{", "]": "["}
    for i, ch in enumerate(masked):
        if ch in "({[":
            stack.append((ch, i))
        elif ch in closers:
            if not stack:
                return pairs, f"an extra `{ch}` on line {_line(masked, i)} has nothing to close"
            o, oi = stack.pop()
            if o != closers[ch]:
                return pairs, f"the `{ch}` on line {_line(masked, i)} doesn't match the `{o}` opened on line {_line(masked, oi)}"
            pairs[oi] = i
    if stack:
        o, oi = stack[-1]
        return pairs, f"the `{o}` opened on line {_line(masked, oi)} is never closed"
    return pairs, None


def _methods(masked: str, pairs: dict[int, int]) -> list[dict]:
    res = []
    for oi, ci in pairs.items():
        if masked[oi] != "{":
            continue
        k = max(masked.rfind(";", 0, oi), masked.rfind("{", 0, oi), masked.rfind("}", 0, oi))
        header = masked[k + 1:oi].strip()
        if not header.endswith(")") and "throws" not in header:
            continue
        if re.search(r"\bnew\b|=|->", header):
            continue
        m = _HDR.match(header)
        if not m or m.group(1) in _CONTROL:
            continue
        res.append(dict(name=m.group(1), open=oi, close=ci, lines=masked.count("\n", oi, ci) + 1, line=_line(masked, oi)))
    return res


def static_review(code: str) -> list[str]:
    """Heuristic coach tips for Java source (no parser). At most 5, most important first."""
    if not code or not code.strip():
        return []
    masked = _mask(code)
    pairs, problem = _pairs(masked)
    if problem:
        return [f"**Brackets don't balance:** {problem}. javac would report `reached end of file while parsing` or "
                "`class, interface, enum, or record expected`; the real mistake is often a line or two above."]
    notes: list[str] = []
    body = re.sub(r"(?m)^\s*(?:import|package)\b[^\n]*", lambda m: " " * len(m.group(0)), masked)
    svars = set(re.findall(r"\bString\s+(\w+)\b(?!\s*\()", masked)) | set(re.findall(r"\bvar\s+(\w+)\s*=\s*\"", masked))
    ivars = set(re.findall(r"\b(?:int|long|short)\s+(\w+)", masked))
    methods = _methods(masked, pairs)

    # -- control statements: stray ';' and missing braces
    stray, nobrace = [], []
    n = len(masked)
    for m in re.finditer(r"\b(if|for|while)\s*\(", masked):
        close = pairs.get(m.end() - 1)
        if close is None:
            continue
        k = close + 1
        while k < n and masked[k].isspace():
            k += 1
        nxt = masked[k] if k < n else ""
        if nxt == "{" or nxt == "":
            continue
        if nxt == ";":
            if m.group(1) in ("if", "for"):
                stray.append((m.group(1), _line(masked, m.start())))
            continue
        nobrace.append((m.group(1), _line(masked, m.start())))
    for m in re.finditer(r"\belse\b\s*(?!\{|if\b)\S", masked):
        nobrace.append(("else", _line(masked, m.start())))
    if stray:
        kw, ln = stray[0]
        notes.append(f"Line {ln}: a `;` right after `{kw} (...)` makes the body empty, so the block below it always runs. Remove that `;`.")

    # -- == / != on strings
    str_eq = bool(re.search(r"(?:\w|\))\s*(?:==|!=)\s*\"|\"\s*(?:==|!=)", masked))
    if not str_eq:
        for m in re.finditer(r"\b(\w+)\s*(?:==|!=)\s*(\w+)\b", masked):
            a, b = m.group(1), m.group(2)
            if (a in svars or b in svars) and not ({a, b} & {"null", "true", "false"}) and not (a.isdigit() or b.isdigit()):
                str_eq = True
                break
    if str_eq:
        notes.append("`==` on Strings compares *identity*, not letters; it can look right and then fail on real input. Use `a.equals(b)` "
                     "(or `\"literal\".equals(x)` to stay null-safe).")

    # -- empty / noisy catch
    if re.search(r"catch\s*\([^)]*\)\s*\{\s*\}", masked):
        notes.append("An **empty `catch`** swallows the error silently. At least log it, rethrow it, or handle it on purpose (and say why in a comment).")
    if re.search(r"catch\s*\(\s*(?:final\s+)?(?:Exception|Throwable)\s+\w+\s*\)", masked):
        notes.append("Catching `Exception`/`Throwable` is too broad and hides real bugs. Catch the narrowest type that makes sense (`NumberFormatException`, `IOException`...).")
    if re.search(r"catch\s*\([^)]*\)\s*\{\s*\w+\.printStackTrace\(\)\s*;\s*\}", masked):
        notes.append("`e.printStackTrace()` alone isn't error handling. Log it with a logger, or recover/rethrow.")

    # -- integer division assigned to a double
    dvars = set(re.findall(r"\b(?:double|float)\s+(\w+)", masked))
    for m in re.finditer(r"(?:\b(?:double|float)\s+)?\b(\w+)\s*=\s*(\w+)\s*/\s*(\w+)\s*;", masked):
        lhs, a, b = m.groups()
        if lhs in dvars and all(x in ivars or re.fullmatch(r"\d+", x) for x in (a, b)):
            notes.append(f"`{lhs} = {a} / {b};` divides two ints *first*, so the fraction is lost before it reaches the `double`. "
                         f"Cast one side: `(double) {a} / {b}`.")
            break

    # -- missing braces
    if nobrace:
        kw, ln = nobrace[0]
        more = f" (and {len(nobrace) - 1} more)" if len(nobrace) > 1 else ""
        notes.append(f"Line {ln}: `{kw}` without braces{more}. It works today, but the day someone adds a second line it silently isn't part of the `{kw}`. Always use `{{ }}`.")

    # -- System.exit outside main
    for m in re.finditer(r"System\s*\.\s*exit\s*\(", masked):
        inside = [x for x in methods if x["open"] < m.start() < x["close"]]
        if inside and min(inside, key=lambda x: x["close"] - x["open"])["name"] != "main":
            notes.append("`System.exit(...)` inside a helper method kills the whole JVM (no `finally`, tests die too). Return a result or throw an exception, and call `exit` at most once in `main`.")
            break

    # -- string concatenation in loops
    for m in re.finditer(r"\b(?:for|while)\s*\(", masked):
        close = pairs.get(m.end() - 1)
        if close is None:
            continue
        k = close + 1
        while k < n and masked[k].isspace():
            k += 1
        if k < n and masked[k] == "{" and k in pairs:
            seg = masked[k:pairs[k]]
            hit = [v for v in re.findall(r"\b(\w+)\s*\+=", seg) if v in svars] or \
                  [v for v in re.findall(r"\b(\w+)\s*=\s*\1\s*\+", seg) if v in svars]
            if hit:
                notes.append(f"Building `{hit[0]}` with `+=` inside a loop copies the whole text every round. Use a `StringBuilder` and `append(...)`, then `toString()` once.")
                break

    # -- boolean compared with true/false
    if re.search(r"(?:==|!=)\s*(?:true|false)\b", masked):
        notes.append("Compare booleans directly: write `if (flag)` / `if (!flag)` instead of `if (flag == true)`.")

    # -- raw types
    for m in re.finditer(rf"(?<![\w.@])({_RAW})\b(?!\s*[<.:])", body):
        before = body[max(0, m.start() - 12):m.start()]
        if re.search(r"instanceof\s*$", before):
            continue
        notes.append(f"`{m.group(1)}` is used without a type argument (a *raw type*), so the compiler can't protect you. Write `{m.group(1)}<String>` / `new {m.group(1)}<>()`.")
        break

    # -- placeholders and deprecated boxing constructors
    if "TODO" in code:
        notes.append("There are still `TODO` placeholders, so some methods probably return default values (`0`, `null`, `false`).")
    if re.search(r"\bnew\s+(?:Integer|Double|Long|Boolean|Character|Short|Byte|Float)\s*\(", masked):
        notes.append("`new Integer(...)` and friends are deprecated for removal. Use `Integer.valueOf(...)` or just autoboxing.")

    # -- public fields
    pm = re.search(r"(?:^|(?<=[;{}]))[ \t]*public[ \t]+(?!static[ \t]+final\b)(?!final\b)(?:static[ \t]+)?(?!class\b|interface\b|enum\b|record\b|abstract\b|void\b)"
                   r"[\w.]+(?:<[^;=(){}]*>)?(?:\[\])*[ \t]+(\w+)[ \t]*(?:=[^;]*)?;", masked, re.M)  # noqa: E501
    if pm:
        notes.append(f"`{pm.group(1)}` is a `public` field. Make it `private` and expose it through a method, so the class controls its own rules (encapsulation).")

    # -- unused imports (by name; a mention anywhere else, even in a comment, counts as use)
    rest = re.sub(r"(?m)^\s*import\b[^\n]*", "", code)
    unused = []
    for m in re.finditer(r"(?m)^\s*import\s+(?:static\s+)?[\w.]+\.(\w+)\s*;", code):
        if not re.search(rf"\b{re.escape(m.group(1))}\b", rest):
            unused.append(m.group(1))
    if unused:
        notes.append(f"Unused import{'s' if len(unused) > 1 else ''}: {', '.join('`' + u + '`' for u in unused[:3])}. Remove what you don't use (IDE: *Optimize Imports*).")

    # -- very long methods
    for md in methods:
        if md["lines"] > 30:
            notes.append(f"`{md['name']}` is {md['lines']} lines long. Split it into smaller methods with names that say what each step does.")
            break

    # -- magic numbers
    magic: list[str] = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s or s.startswith("@") or re.search(r"\bfinal\b|\bcase\b|\bdefault\b", s):
            continue
        if re.match(r"^(?:[\w<>\[\],.?]+\s+)+\w+\s*=\s*-?[\d._]+[lLfFdD]?\s*;$", s) or re.match(r"^return\s+-?\d+\s*;$", s):
            continue
        if re.search(r"=\s*\{|new\s+\w+(?:\[\])+\s*\{|\[\s*\d+\s*\]", s):
            continue
        for nm in re.finditer(r"(?:[*/%<>+-]=?|==|!=)\s*(\d+\.\d+|\d+)[lLfFdD]?(?![\w.])", s):
            val = nm.group(1)
            norm = str(float(val)).rstrip("0").rstrip(".") if "." in val else val
            if norm not in _PRIMS_OK and val not in magic:
                magic.append(val)
    if magic:
        show = ", ".join(f"`{v}`" for v in magic[:3])
        notes.append(f"Magic numbers like {show} are hard to understand. Give them a name: `private static final double TAX_RATE = 0.18;`.")

    # -- one-letter names
    singles: list[str] = []
    for m in re.finditer(r"\b((?:int|long|short|byte|double|float|boolean|char|String|var|[A-Z]\w*(?:<[^<>;(){}=]*(?:<[^<>;(){}=]*>[^<>;(){}=]*)*>)?)(?:\[\])*)"
                         r"\s+([A-Za-z])\s*(?=[=;,):])", masked):
        typ, nm = m.group(1), m.group(2)
        if nm in "ijknxye" or len(typ) == 1 or re.search(r"instanceof\s*$", masked[max(0, m.start() - 12):m.start()]):
            continue
        if nm not in singles:
            singles.append(nm)
    if singles:
        notes.append(f"Single-letter names like `{singles[0]}` make code harder to read; name what it *means* (`total`, `price`, `customer`).")

    return notes[:5]


# =====================================================================================================
# looks_code
# =====================================================================================================
_JAVA_STRONG = [re.compile(p, re.M) for p in (
    r"\bpublic\s+static\s+void\s+main\b",
    r"\bSystem\s*\.\s*(?:out|err)\s*\.\s*print",
    r"^\s*import\s+(?:static\s+)?[\w.]+(?:\.\*)?\s*;",
    r"^\s*package\s+[\w.]+\s*;",
    r"\b(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:abstract\s+)?(?:class|interface|enum|record|void|[\w<>\[\],.?]+)\s+\w+\s*[({=;]",
    r"\b(?:class|interface|enum|record|sealed\s+interface)\s+[A-Z]\w*(?:<[^>]*>)?(?:\s*\([^)]*\))?(?:\s+(?:extends|implements|permits)\s+[\w<>, .]+)?\s*\{",
    r"\b(?:int|long|double|float|boolean|char|byte|short|String|var)(?:\[\])*\s+\w+\s*(?:=|;)",
    r"\bnew\s+[A-Z]\w*(?:<[^>]*>)?\s*[(\[]",
    r"@(?:Override|Test|FunctionalInterface|SuppressWarnings|Autowired|RestController)\b",
    r"\bfor\s*\(\s*(?:int|long|var|[A-Z]\w*(?:<[^>]*>)?)\s+\w+\s*[:=]",
    r"\b(?:try|catch)\s*\(\s*(?:final\s+)?[A-Z]\w*(?:\s*\|\s*[A-Z]\w*)*\s+\w+",
)]
_SQL = re.compile(r"\bSELECT\b.+\bFROM\b", re.I | re.S)


def looks_code(text: str) -> bool:
    """True when `text` looks like Java source (or a SQL query, like the Python `_looks_code`)."""
    if not text or not text.strip():
        return False
    if _SQL.search(text):
        return True
    if any(rx.search(text) for rx in _JAVA_STRONG):
        return True
    # weaker shapes: a statement line ending in ';' that has a call or an assignment, or a "header) {" line
    if re.search(r"^[^\n]*[\w\])]\s*(?:\(|=|\+\+|--|\+=)[^\n]*;\s*$", text, re.M):
        return True
    return bool(re.search(r"\)\s*\{\s*$", text, re.M) and ";" in text)


# =====================================================================================================
# concept keywords / lookup over kb_java
# =====================================================================================================
def concept_keywords() -> dict[str, list[str]]:
    """{entry id: keyword list} for the Java knowledge base (what find_concepts matches questions against)."""
    return {e["id"]: list(e["keys"]) for e in kb_java.KB}


def find_concepts(text: str, selection: str, code: str, day_no: int | None, kb: list[dict] | None = None) -> list[dict]:
    """Same scoring as assistant.find_concepts, over kb_java.KB by default."""
    entries = kb if kb is not None else kb_java.KB
    t, s, c = (text or "").lower(), (selection or "").lower(), (code or "").lower()
    scored = []
    for e in entries:
        sc = 0.0
        for k in e["keys"]:
            kl = k.lower()
            if re.search(r"[^a-z0-9_]", kl):
                hit = lambda hay, kl=kl: kl in hay                       # noqa: E731
            else:
                rx = re.compile(r"(?<![a-z0-9_])" + re.escape(kl) + r"(?:e?s)?(?![a-z0-9_])")
                hit = lambda hay, rx=rx: bool(rx.search(hay))            # noqa: E731
            if hit(t):
                sc += 3
            if hit(s):
                sc += 3
            if hit(c):
                sc += 0.7
        if sc and day_no and day_no in e["days"]:
            sc += 1.5
        if sc:
            scored.append((sc, e))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return []
    top = scored[0][0]
    return [scored[0][1]] + [e for s_, e in scored[1:3] if s_ >= 3 and s_ >= 0.5 * top]


def day_concepts(day_no: int | None, kb: list[dict] | None = None) -> list[dict]:
    return [e for e in (kb if kb is not None else kb_java.KB) if day_no and day_no in e["days"]]
