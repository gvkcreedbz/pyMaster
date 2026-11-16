"""Tests for the Java twin of the tutor knowledge/coaching helpers.

Run (isolated interpreter):  python -m pytest _dev_tools/test_java_assist.py -q -p no:cacheprovider
Covers portal/kb_java.py, portal/java_assist.py and (when a JDK is available) real javac / JVM messages.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True                       # never litter the portal folder with __pycache__
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from portal import java_assist as ja      # noqa: E402
from portal import kb, kb_java            # noqa: E402

REQUIRED = ["id", "name", "days", "keys", "what", "where", "how", "pitfall", "nxt"]
MERMAID_START = ("flowchart", "graph", "sequenceDiagram", "stateDiagram-v2", "classDiagram", "erDiagram", "gantt", "pie", "journey", "mindmap", "timeline")


# =============================================================================================== kb_java
def test_public_names_match_python_kb():
    for name in ("KB", "BY_ID", "GENERIC_USAGE", "VISUALS"):
        assert hasattr(kb_java, name) and hasattr(kb, name)
    assert isinstance(kb_java.KB, list) and isinstance(kb_java.BY_ID, dict)
    assert isinstance(kb_java.GENERIC_USAGE, str) and kb_java.GENERIC_USAGE.strip()
    assert set(kb_java.KB[0]) == set(kb.KB[0])                  # exactly the same dict keys as the Python entries
    assert {tuple(sorted(v)) for v in kb_java.VISUALS.values()} == {tuple(sorted(v)) for v in kb.VISUALS.values()}


def test_at_least_34_entries_with_unique_ids():
    ids = [e["id"] for e in kb_java.KB]
    assert len(ids) >= 34
    assert len(ids) == len(set(ids))
    assert set(kb_java.BY_ID) == set(ids)
    assert all(kb_java.BY_ID[e["id"]] is e for e in kb_java.KB)


@pytest.mark.parametrize("entry", kb_java.KB, ids=lambda e: e["id"])
def test_every_entry_has_all_required_keys(entry):
    assert set(REQUIRED) <= set(entry), f"missing {set(REQUIRED) - set(entry)}"
    assert set(entry) == set(REQUIRED)
    for k in ("id", "name", "what", "where", "how", "pitfall", "nxt"):
        assert isinstance(entry[k], str) and entry[k].strip(), k
    assert entry["keys"] and all(isinstance(k, str) and k.strip() for k in entry["keys"])
    assert entry["days"] and all(isinstance(d, int) and 1 <= d <= 30 for d in entry["days"])


@pytest.mark.parametrize("entry", kb_java.KB, ids=lambda e: e["id"])
def test_entry_voice_and_code_blocks(entry):
    assert entry["where"].lstrip().startswith("- "), "where is a bullet list like the Python entries"
    assert entry["where"].count("\n- ") >= 2 and "**" in entry["where"]
    assert entry["how"].lstrip().startswith("```") and entry["how"].count("```") % 2 == 0
    assert re.search(r"```(java|xml|text)\n", entry["how"])
    assert len(entry["what"]) > 60 and len(entry["pitfall"]) > 40


def test_every_course_day_is_covered():
    covered = {d for e in kb_java.KB for d in e["days"]}
    assert covered >= set(range(1, 31)), f"days without a concept: {sorted(set(range(1, 31)) - covered)}"


def test_syllabus_topics_are_present():
    names = " ".join(e["name"].lower() + " " + " ".join(e["keys"]) for e in kb_java.KB)
    for topic in ["stringbuilder", "scanner", "arraylist", "hashmap", "hashset", "lambda", "stream", "record", "optional", "regex", "junit",
                  "groupingby", "httpclient", "jdbc", "spring", "thread", "logging", "maven", "try-with-resources", "sealed", "enum", "generic",
                  "csv", "printf", "switch", "equals"]:
        assert topic in names, topic


def test_visuals_are_valid_mermaid_text():
    assert len(kb_java.VISUALS) >= 25
    for key, v in kb_java.VISUALS.items():
        assert key in kb_java.BY_ID, f"visual {key} has no KB entry"
        assert set(v) == {"title", "caption", "mermaid"}
        assert all(isinstance(v[k], str) and v[k].strip() for k in v), key
        first = v["mermaid"].strip().split()[0]
        assert first.startswith(MERMAID_START), (key, first)
        assert v["mermaid"].count('"') % 2 == 0, f"{key}: unbalanced quotes"
        assert ";" not in v["mermaid"], f"{key}: ';' is a statement separator in Mermaid"
        for o, c in ("()", "[]", "{}"):
            assert v["mermaid"].count(o) == v["mermaid"].count(c), f"{key}: unbalanced {o}{c}"


def test_visuals_conservative_syntax():
    for key, v in kb_java.VISUALS.items():
        m = v["mermaid"]
        if m.startswith("stateDiagram"):
            for ln in m.splitlines():
                if "-->" in ln and ":" in ln:
                    assert ln.count(":") == 1, f"{key}: colon inside a stateDiagram label: {ln}"
        assert "#" not in m, key
        if m.startswith("flowchart"):
            assert not re.search(r"(?<![\w])end(?![\w])\s*[\[\(\{]", m), f"{key}: node id 'end' breaks Mermaid"
            assert "<" not in re.sub(r"<br/>", "", m), f"{key}: raw '<' in a label"


def test_concepts_found_by_questions():
    cases = {
        "where is HashMap used in real projects": "hashmap",
        "why does == fail when comparing strings": "equals_ref",
        "how do I read a file with Files.readAllLines": "files_nio",
        "explain try-with-resources": "try_resources",
        "what is a lambda": "lambdas",
        "how do I use groupingBy": "collectors",
    }
    for q, want in cases.items():
        got = ja.find_concepts(q, "", "", None)
        assert got and got[0]["id"] == want, (q, [g["id"] for g in got])
    assert ja.find_concepts("zzz qqq", "", "", None) == []


def test_day_concepts_and_keyword_hook():
    d11 = [e["id"] for e in ja.day_concepts(11)]
    assert "methods" in d11
    assert ja.day_concepts(None) == []
    ck = ja.concept_keywords()
    assert set(ck) == set(kb_java.BY_ID) and all(isinstance(v, list) and v for v in ck.values())
    assert "hashmap" in ck["hashmap"]


# ============================================================================================ decode_error
COMPILE_CASES = [
    ("Main.java:5: error: cannot find symbol\n        int y = x + 1;\n                ^\n  symbol:   variable x\n  location: class Main", ["cannot find symbol", "`x`"]),
    ("Main.java:3: error: cannot find symbol\n  Scanner in = new Scanner(System.in);\n  ^\n  symbol:   class Scanner\n  location: class Main", ["import java.util.Scanner;"]),
    ("Main.java:7: error: cannot find symbol\n    s.size();\n     ^\n  symbol:   method size()\n  location: variable s of type String", ["method"]),
    ("Main.java:4: error: ';' expected\n        int x = 5\n                 ^", ["';' expected", "add `;`"]),
    ("Main.java:6: error: ')' expected\n    System.out.println(\"a\";", ["`)`"]),
    ("Main.java:6: error: ')' or ',' expected\n    foo(1;", ["`)`"]),
    ("Main.java:4: error: incompatible types: possible lossy conversion from double to int\n        int x = 3.5;\n                ^", ["lossy", "(int)"]),
    ("Main.java:4: error: incompatible types: String cannot be converted to int\n        int x = \"5\";", ["incompatible types", "parseInt"]),
    ("Main.java:9: error: missing return statement\n    }\n    ^", ["missing return statement"]),
    ("Main.java:1: error: class Shop is public, should be declared in a file named Shop.java\npublic class Shop {", ["Shop.java"]),
    ("Main.java:3: error: unclosed string literal\n    System.out.println(\"hi);", ["unclosed string literal", "closing"]),
    ("Main.java:5: error: non-static method greet() cannot be referenced from a static context\n    greet();", ["static", "greet"]),
    ("Main.java:6: error: variable total might not have been initialized\n    System.out.println(total);", ["initialized", "total"]),
    ("Main.java:8: error: unreported exception IOException; must be caught or declared to be thrown\n    Files.readAllLines(p);", ["throws IOException", "try"]),
    ("Main.java:8: error: unreachable statement", ["unreachable"]),
    ("Main.java:2: error: package org.foo does not exist", ["package org.foo"]),
    ("Main.java:4: error: variable x is already defined in method main(String[])", ["already defined"]),
    ("Main.java:4: error: cannot assign a value to final variable MAX", ["final"]),
    ("Main.java:4: error: bad operand types for binary operator '+'\n  first type: int\n  second type: boolean", ["bad operand"]),
    ("Main.java:4: error: int cannot be dereferenced", ["dereferenced", "primitive"]),
    ("Main.java:30: error: reached end of file while parsing\n}\n ^", ["reached end of file", "braces"]),
    ("Error: Could not find or load main class Hello\nCaused by: java.lang.ClassNotFoundException: Hello", ["main class"]),
]

RUNTIME_CASES = [
    ('Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.length()" because "name" is null\n\tat Main.main(Main.java:5)', ["NullPointerException", "name", "null"]),
    ('Exception in thread "main" java.lang.NullPointerException: Cannot invoke "java.lang.Integer.intValue()" because the return value of "java.util.Map.get(Object)" is null\n\tat Main.main(Main.java:9)', ["getOrDefault"]),
    ('Exception in thread "main" java.lang.NullPointerException\n\tat Main.main(Main.java:5)', ["null"]),
    ('Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 3\n\tat Main.main(Main.java:6)', ["index 5", "3 elements", "0 to 2"]),
    ('Exception in thread "main" java.lang.StringIndexOutOfBoundsException: begin 0, end 10, length 5\n\tat java.base/java.lang.String.checkBoundsBeginEnd(String.java:4606)', ["substring(0, 10)", "length 5"]),
    ('Exception in thread "main" java.lang.StringIndexOutOfBoundsException: Index 9 out of bounds for length 4', ["charAt(9)"]),
    ('Exception in thread "main" java.lang.IndexOutOfBoundsException: Index 3 out of bounds for length 3\n\tat java.base/jdk.internal.util.Preconditions.outOfBounds(Preconditions.java:100)', ["index 3", "size()"]),
    ('Exception in thread "main" java.lang.ArithmeticException: / by zero\n\tat Main.divide(Main.java:12)', ["divided", "zero"]),
    ('Exception in thread "main" java.lang.ClassCastException: class java.lang.String cannot be cast to class java.lang.Integer (java.lang.String and java.lang.Integer are in module java.base of loader \'bootstrap\')', ["`String`", "`Integer`"]),
    ('Exception in thread "main" java.lang.NumberFormatException: For input string: "abc"\n\tat java.base/java.lang.NumberFormatException.forInputString(NumberFormatException.java:67)', ['"abc"', "parseInt"]),
    ('Exception in thread "main" java.util.InputMismatchException\n\tat java.base/java.util.Scanner.throwFor(Scanner.java:939)', ["nextInt", "nextLine"]),
    ('Exception in thread "main" java.util.NoSuchElementException: No line found\n\tat java.base/java.util.Scanner.nextLine(Scanner.java:1660)', ["no more input", "hasNextLine"]),
    ('Exception in thread "main" java.util.NoSuchElementException: No value present', ["Optional"]),
    ('Exception in thread "main" java.util.ConcurrentModificationException\n\tat java.base/java.util.ArrayList$Itr.checkForComodification(ArrayList.java:1095)', ["removeIf", "Iterator"]),
    ('Exception in thread "main" java.lang.StackOverflowError\n\tat Main.f(Main.java:3)', ["base case"]),
    ('Exception in thread "main" java.lang.OutOfMemoryError: Java heap space', ["memory", "Files.lines"]),
    ('Exception in thread "main" java.lang.UnsupportedOperationException\n\tat java.base/java.util.ImmutableCollections.uoe(ImmutableCollections.java:142)', ["read-only"]),
    ('Exception in thread "main" java.nio.file.NoSuchFileException: data/sales.csv', ["sales.csv", "working directory"]),
]


@pytest.mark.parametrize("text,needles", COMPILE_CASES + RUNTIME_CASES)
def test_decode_error_recognises(text, needles):
    out = ja.decode_error(text)
    assert out, text
    low = out.lower()
    for n in needles:
        assert n.lower() in low, (n, out)


def test_decode_error_format_matches_python_helper():
    out = ja.decode_error("Main.java:5: error: missing return statement")
    first = out.splitlines()[0]
    assert first.startswith("- `") and "**" in first and "Typical fix:" in first
    assert len(out.splitlines()) <= 2


def test_decode_error_none_and_fallback():
    assert ja.decode_error("") is None
    assert ja.decode_error("   \n") is None
    assert ja.decode_error("my program prints the wrong total, why?") is None
    out = ja.decode_error('Exception in thread "main" com.shop.PaymentDeclinedException: card 4242')
    assert out and "PaymentDeclinedException" in out and "first line" in out


def test_decode_error_reports_line_numbers():
    out = ja.decode_error("Main.java:12: error: missing return statement\n}")
    assert "Main.java, line 12" in out
    out = ja.decode_error('Exception in thread "main" java.lang.ArithmeticException: / by zero\n'
                          '\tat java.base/java.lang.Integer.divideUnsigned(Integer.java:1)\n\tat Shop.avg(Shop.java:21)\n\tat Shop.main(Shop.java:8)')
    assert "Shop.java, line 21" in out


def test_decode_error_caps_two_bullets_in_order_of_appearance():
    text = ("Main.java:3: error: cannot find symbol\n  symbol:   variable a\nMain.java:5: error: ';' expected\n"
            "Main.java:9: error: missing return statement\n")
    out = ja.decode_error(text).splitlines()
    assert len(out) == 2 and "cannot find symbol" in out[0] and "';' expected" in out[1]


def test_checked_exception_is_not_reported_twice():
    out = ja.decode_error("Main.java:8: error: unreported exception FileNotFoundException; must be caught or declared to be thrown")
    assert out.count("\n") == 0 and "unreported exception" in out


def test_looks_like_error():
    assert ja.looks_like_error("Main.java:3: error: ';' expected")
    assert ja.looks_like_error('Exception in thread "main" java.lang.NullPointerException')
    assert not ja.looks_like_error("how do I print a list?")


# ============================================================================================ static_review
BAD = '''import java.util.*;
import java.io.File;

public class Shop {
    public int total;
    static void go(String a, String b) {
        if (a == b) System.out.println("same");
        String report = "";
        for (int i = 0; i < 5; i++) {
            report += i;
        }
        try {
            Integer.parseInt(a);
        } catch (Exception e) {
        }
        List items = new ArrayList();
        double avg = total / 4;
        System.exit(1);
    }
}
'''


def test_static_review_finds_many_problems_but_caps_at_five():
    notes = ja.static_review(BAD)
    assert 1 <= len(notes) <= 5
    assert any("==" in n and "equals" in n for n in notes), notes


@pytest.mark.parametrize("snippet,needle", [
    ('class A { boolean f(String s) { return s == "yes"; } }', "equals"),
    ('class A { void f(String a, String b) { if (a != b) { } } }', "equals"),
    ('class A { void f(int x) { if (x > 1) System.out.println(x); } }', "without braces"),
    ('class A { void f(int x) { if (x > 1);\n { } } }', "`;`"),
    ('class A { void f() { try { run(); } catch (Exception e) { } } }', "empty `catch`"),
    ('class A { void f() { try { run(); } catch (IOException e) { e.printStackTrace(); } } }', "printStackTrace"),
    ('class A { void f() { try { run(); } catch (Exception e) { log(e); } } }', "too broad"),
    ('class A { void f(boolean ok) { if (ok == true) { } } }', "directly"),
    ('class A { void f() { List xs = new ArrayList(); } }', "raw type"),
    ('class A { double f(int a, int b) { double r = a / b; return r; } }', "(double) a / b"),
    ('class A { void f() { String s = ""; for (int i = 0; i < n; i++) { s += i; } } }', "StringBuilder"),
    ('class A { void f() { System.exit(2); } }', "System.exit"),
    ('class A {\n    public int count;\n}', "public"),
    ('class A { public String name = "x"; }', "private"),
    ('import java.util.List;\nclass A { }', "Unused import"),
    ('class A { double f(double p) { return p * 1.18; } }', "Magic numbers"),
    ('class A { void f() { int q = 3; } }', "Single-letter"),
    ('class A { void f() { // TODO finish\n } }', "TODO"),
    ('class A { void f() { Integer i = new Integer(5); } }', "deprecated"),
])
def test_static_review_individual_tips(snippet, needle):
    notes = ja.static_review(snippet)
    assert any(needle.lower() in n.lower() for n in notes), (needle, notes)


def test_static_review_long_method():
    body = "\n".join(f"        total += {i % 2};" for i in range(40))
    code = f"class A {{\n    static int sum() {{\n        int total = 0;\n{body}\n        return total;\n    }}\n}}\n"
    assert any("`sum` is" in n and "lines long" in n for n in ja.static_review(code))


def test_static_review_clean_code_has_no_notes():
    clean = '''import java.util.List;

public class Cart {
    private static final double TAX_RATE = 0.18;
    private final List<Double> prices;

    public Cart(List<Double> prices) {
        this.prices = List.copyOf(prices);
    }

    public double total() {
        double sum = 0;
        for (double price : prices) {
            sum += price;
        }
        return sum * (1 + TAX_RATE);
    }

    public static void main(String[] args) {
        String name = "chai";
        if ("chai".equals(name)) {
            System.out.println(new Cart(List.of(10.0, 20.0)).total());
        }
    }
}
'''
    assert ja.static_review(clean) == []


def test_static_review_ignores_comments_and_strings():
    code = ('class A {\n  // if (a == "x") System.exit(1);\n  /* catch (Exception e) { } */\n'
            '  String text = "if (x) y; { catch (Exception e) {} == \\"z\\" 1.18 * 77";\n  void f() { }\n}\n')
    assert ja.static_review(code) == []


def test_static_review_unbalanced_braces_returns_single_note():
    notes = ja.static_review("class A {\n  void f() {\n    int x = 1;\n}\n")
    assert len(notes) == 1 and "balance" in notes[0].lower() and "line 1" in notes[0]
    notes = ja.static_review("class A { void f() { foo(1; } }")
    assert len(notes) == 1 and "doesn't match" in notes[0]


def test_static_review_empty_input():
    assert ja.static_review("") == []
    assert ja.static_review("   \n\n") == []


# =================================================================================================== looks_code
@pytest.mark.parametrize("text", [
    "int x = 5;",
    'System.out.println("hi")',
    "public class Hello {\n  public static void main(String[] args) { }\n}",
    "import java.util.*;",
    "List<String> names = new ArrayList<>();",
    "for (int i = 0; i < 3; i++) {\n  total += i;\n}",
    "record Item(String name, double price) {}",
    "SELECT region, SUM(amt) FROM sales GROUP BY region",
    '@Override\npublic String toString() { return "x"; }',
    "try (var in = Files.newBufferedReader(p)) {\n}",
])
def test_looks_code_true(text):
    assert ja.looks_code(text) is True


@pytest.mark.parametrize("text", [
    "", "   ", "hello", "Where is a HashMap used?", "what does static mean",
    "def f(x):\n    return x", "x = 5", "print('hi')", "I don't understand loops",
])
def test_looks_code_false(text):
    assert ja.looks_code(text) is False


# ============================================================================== real javac / JVM (optional)
def _jdk_bin(name):
    for home in (os.environ.get("JAVA_HOME"), str(ROOT / ".tools" / "jdk21")):
        if home:
            p = Path(home) / "bin" / (name + (".exe" if os.name == "nt" else ""))
            if p.is_file():
                return str(p)
    return shutil.which(name)


needs_jdk = pytest.mark.skipif(not (_jdk_bin("javac") and _jdk_bin("java")), reason="no JDK found")

REAL_COMPILE = [
    ("class Main { public static void main(String[] a) { int y = x + 1; } }", "cannot find symbol"),
    ("class Main { public static void main(String[] a) { int y = 5 } }", "';' expected"),
    ("class Main { public static void main(String[] a) { int y = 3.5; } }", "lossy"),
    ("class Main { static int f(int a) { if (a > 0) { return 1; } } public static void main(String[] a) { } }", "missing return statement"),
    ("class Main { public static void main(String[] a) { String s = \"hi); } }", "unclosed string literal"),
    ("class Main { int n; public static void main(String[] a) { n = 3; } }", "static"),
    ("class Main { public static void main(String[] a) { int z; System.out.println(z); } }", "might not have been initialized"),
    ("class Main { public static void main(String[] a) { Thread.sleep(10); } }", "unreported exception"),
    ("class Main { public static void main(String[] a) { int n = 4; n.toString(); } }", "dereferenced"),
]
REAL_RUNTIME = [
    ("String s = null; System.out.println(s.length());", "NullPointerException"),
    ("int[] a = new int[3]; a[5] = 1;", "index 5"),
    ('System.out.println("hello".substring(2, 9));', "substring"),
    ("int z = 0; System.out.println(10 / z);", "zero"),
    ('Object o = "x"; Integer i = (Integer) o;', "ClassCastException"),
    ('Integer.parseInt("abc");', '"abc"'),
    ("java.util.Optional.empty().get();", "Optional"),
    ("var l = new java.util.ArrayList<>(java.util.List.of(1, 2, 3)); for (var x : l) l.remove(x);", "removeIf"),
    ("java.util.List.of(1).add(2);", "read-only"),
    ("java.nio.file.Files.readAllLines(java.nio.file.Path.of(\"nope.txt\"));", "working directory"),
    ("new java.util.Scanner(System.in).nextLine();", "hasNextLine"),
]


@needs_jdk
@pytest.mark.parametrize("src,needle", REAL_COMPILE)
def test_real_javac_messages_are_decoded(tmp_path, src, needle):
    f = tmp_path / "Main.java"
    f.write_text(src, encoding="utf-8")
    r = subprocess.run([_jdk_bin("javac"), "-encoding", "UTF-8", str(f)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
    assert r.returncode != 0, "snippet was supposed to fail to compile"
    out = ja.decode_error(r.stderr)
    assert out, r.stderr
    assert needle.lower() in out.lower(), (needle, out, r.stderr)
    assert "Main.java, line 1" in out


@needs_jdk
@pytest.mark.parametrize("stmt,needle", REAL_RUNTIME)
def test_real_jvm_stack_traces_are_decoded(tmp_path, stmt, needle):
    f = tmp_path / "Main.java"
    f.write_text("class Main {\n  public static void main(String[] args) throws Exception {\n    " + stmt + "\n  }\n}\n", encoding="utf-8")
    r = subprocess.run([_jdk_bin("java"), str(f)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90, input="", cwd=str(tmp_path))
    assert r.returncode != 0, r.stdout
    out = ja.decode_error(r.stderr)
    assert out, r.stderr
    assert needle.lower() in out.lower(), (needle, out, r.stderr)
