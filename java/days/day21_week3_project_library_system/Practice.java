/* Day 21 - Week 3 Project: Library Management System.
 *
 * Run the checks:  java Practice.java
 * Rules: loan period 14 days, late fee Rs. 5 per late day, max 3 active loans per member.
 * Dates are text "YYYY-MM-DD". The checks only use a temporary folder that is deleted at the end.
 * Everything is in this file: read the given parts, then fill in every TODO from top to bottom.
 */
import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;
class Practice {
    static final int LOAN_DAYS = 14;
    static final int FEE_PER_DAY = 5;
    static final int MAX_LOANS = 3;
    /** Raised when a library rule is broken. (given - do not edit) */
    static class LibraryError extends RuntimeException {
        LibraryError(String message) {
            super(message);
        }
    }
    /** One active loan: which book, which member, and the day it went out. (given - do not edit) */
    record Loan(String isbn, String member, String out) {
    }
    // ---------------------------------------------------------------------------
    // L1-1 | Book   (Level 1 - Beginner)
    // Write  record Book(String isbn, String title, String author, int copies)  with
    //   a second constructor Book(isbn, title, author) that means ONE copy (hint: this(..., 1);)
    //   Book withMoreCopies(int more)   returns a NEW Book with copies + more (records never change)
    // ---------------------------------------------------------------------------
    // TODO: write your code here
    record Book(String isbn, String title, String author, int copies) { Book(String isbn, String title, String author) { this(isbn, title, author, 0); } Book withMoreCopies(int more) { return this; } }
    /** The library. The fields are given: read them, then write the methods. */
    static class Library {
        private final Map<String, Book> books = new TreeMap<>();            // isbn -> Book
        private final List<Loan> loans = new ArrayList<>();                  // active loans
        private final Map<String, Integer> checkoutCounts = new TreeMap<>(); // isbn -> times borrowed
        // -----------------------------------------------------------------------
        // L1-2 | addBook and find   (Level 1 - Beginner)
        // addBook(book): if the isbn is new store the book; if it already exists ADD
        //   book.copies() to the stored book's copies (use withMoreCopies).
        // find(text): the TITLES that contain text (ignore capitals), sorted A-Z.
        // -----------------------------------------------------------------------
        void addBook(Book book) {
            // TODO: write your code here
        }
        List<String> find(String text) {
            // TODO: write your code here
            return null;
        }
        // -----------------------------------------------------------------------
        // L1-3 | availableCopies   (Level 1 - Beginner)
        // The copies of the isbn that are NOT currently on loan (0 for an unknown isbn).
        // -----------------------------------------------------------------------
        int availableCopies(String isbn) {
            // TODO: write your code here
            return -1;
        }
        // -----------------------------------------------------------------------
        // L2-1 | checkout   (Level 2 - Intermediate)
        // checkout(isbn, member, dateText). Check in this order and throw a LibraryError:
        //   unknown isbn -> "Unknown book"; no free copy -> "No copies available";
        //   the member already holds MAX_LOANS (3) books -> "Loan limit reached".
        // Otherwise record the loan (new Loan(isbn, member, dateText)) and add 1 to
        // checkoutCounts for that isbn.
        // -----------------------------------------------------------------------
        void checkout(String isbn, String member, String dateText) {
            // TODO: write your code here
        }
        // -----------------------------------------------------------------------
        // L2-2 | returnBook   (Level 2 - Intermediate)
        // returnBook(isbn, member, dateText): find that member's loan for the isbn (none ->
        // throw new LibraryError("No such loan")), remove it, and RETURN the late fee:
        // late days = days between the out-date and dateText MINUS LOAN_DAYS (never below 0),
        // times FEE_PER_DAY.   Hint: ChronoUnit.DAYS.between(LocalDate.parse(a), LocalDate.parse(b))
        // -----------------------------------------------------------------------
        int returnBook(String isbn, String member, String dateText) {
            // TODO: write your code here
            return -1;
        }
        // -----------------------------------------------------------------------
        // L2-3 | save and load   (Level 2 - Intermediate)
        // save(path) writes ONE text line per fact (in this order: all books by isbn, then the loans
        // in the order they were made, then the counts by isbn). Separator is the pipe |
        //     BOOK|111|Python 101|Guido|2
        //     LOAN|111|aarav|2026-11-01
        //     COUNT|111|1
        // load(path) is a STATIC method that builds a NEW Library from such a file. It skips empty
        // lines and throws new LibraryError("Bad line: " + line) for any other kind of line.
        // Hints: Files.write(path, lines), Files.readAllLines(path), line.split("\\|").
        // -----------------------------------------------------------------------
        void save(Path path) throws IOException {
            // TODO: write your code here
        }
        static Library load(Path path) throws IOException {
            // TODO: write your code here
            return null;
        }
        // -----------------------------------------------------------------------
        // L3-1 | overdueReport   (Level 3 - Challenge)
        // The lines for every ACTIVE loan that is more than 14 days old on todayText, formatted
        //   "member: title (N days late)"   with N = days out - 14.   Sorted A-Z.
        // -----------------------------------------------------------------------
        List<String> overdueReport(String todayText) {
            // TODO: write your code here
            return null;
        }
        // -----------------------------------------------------------------------
        // L3-2 | popularBooks   (Level 3 - Challenge)
        // The titles of the n most borrowed books (use checkoutCounts), most borrowed first;
        // equal counts -> title A-Z. Only books borrowed at least once.
        // -----------------------------------------------------------------------
        List<String> popularBooks(int n) {
            // TODO: write your code here
            return null;
        }
    }
    // ======================= AUTO-CHECKER (do not edit below) ====================
    static String errorOf(Runnable action) {
        try {
            action.run();
        } catch (Throwable e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
        return "no error";
    }
    static Library sampleLibrary() {
        Library lib = new Library();
        lib.addBook(new Book("111", "Python 101", "Guido", 2));
        lib.addBook(new Book("222", "Learning Data", "Wes"));
        lib.addBook(new Book("333", "Python Tricks", "Dan"));
        lib.addBook(new Book("444", "Cooking Basics", "Ana"));
        return lib;
    }
    static void deleteFolder(Path folder) throws IOException {
        try (var files = Files.list(folder)) {
            for (Path file : files.toList()) {
                Files.deleteIfExists(file);
            }
        }
        Files.deleteIfExists(folder);
    }
    /** save and load in a temporary folder (checked exceptions cannot cross a lambda, so catch them here). */
    static Object saveAndLoad() {
        Path folder = null;
        try {
            folder = Files.createTempDirectory("library");
            Library lib = sampleLibrary();
            lib.checkout("111", "aarav", "2026-11-01");
            lib.checkout("222", "diya", "2026-11-02");
            Path file = folder.resolve("library.txt");
            lib.save(file);
            List<String> saved = Files.readAllLines(file);
            Library again = Library.load(file);
            return List.of(saved, again.books.equals(lib.books), again.loans.equals(lib.loans),
                    again.checkoutCounts.equals(lib.checkoutCounts), again.availableCopies("111"));
        } catch (IOException e) {
            return "IOException: " + e.getMessage();
        } finally {
            try {
                if (folder != null) {
                    deleteFolder(folder);
                }
            } catch (IOException ignored) {
                // the temp folder is cleaned by the operating system later
            }
        }
    }
    static Object loadHandWrittenFile(String text) {
        Path folder = null;
        try {
            folder = Files.createTempDirectory("library");
            Path file = folder.resolve("hand.txt");
            Files.writeString(file, text);
            Library lib = Library.load(file);
            return List.of(lib.find(""), lib.availableCopies("111"), lib.returnBook("111", "aarav", "2026-11-20"));
        } catch (IOException e) {
            return "IOException: " + e.getMessage();
        } catch (LibraryError e) {
            return "LibraryError: " + e.getMessage();
        } finally {
            try {
                if (folder != null) {
                    deleteFolder(folder);
                }
            } catch (IOException ignored) {
                // see above
            }
        }
    }
    public static void main(String[] args) {
        System.out.println("--- Day 21 checks ---");
        Checker.check("L1-1 Book record", () -> List.of(new Book("1", "T", "A").copies(), new Book("1", "T", "A", 3).copies(),
                new Book("1", "T", "A").equals(new Book("1", "T", "A", 1)), new Book("1", "T", "A").title()), List.of(1, 3, true, "T"));
        Checker.check("L1-1 Book.withMoreCopies", () -> {
            Book original = new Book("1", "T", "A", 2);
            Book more = original.withMoreCopies(3);
            return List.of(more.copies(), original.copies(), more.isbn());
        }, List.of(5, 2, "1"));
        Checker.check("L1-2 addBook merges copies / find", () -> {
            Library lib = sampleLibrary();
            lib.addBook(new Book("111", "Python 101", "Guido", 3));
            return List.of(lib.books.get("111").copies(), lib.find("PYTHON"), lib.find("data"), lib.find("zzz"));
        }, List.of(5, List.of("Python 101", "Python Tricks"), List.of("Learning Data"), List.of()));
        Checker.check("L1-3 availableCopies", () -> {
            Library lib = sampleLibrary();
            int before = lib.availableCopies("111");
            lib.checkout("111", "aarav", "2026-11-01");
            return List.of(before, lib.availableCopies("111"), lib.availableCopies("999"));
        }, List.of(2, 1, 0));
        Checker.check("L2-1 checkout rules", () -> {
            Library lib = sampleLibrary();
            List<Object> out = new ArrayList<>();
            out.add(errorOf(() -> lib.checkout("999", "aarav", "2026-11-01")));
            lib.checkout("222", "aarav", "2026-11-01");
            out.add(errorOf(() -> lib.checkout("222", "diya", "2026-11-01")));
            lib.checkout("111", "aarav", "2026-11-01");
            lib.checkout("333", "aarav", "2026-11-01");
            out.add(errorOf(() -> lib.checkout("444", "aarav", "2026-11-01")));
            out.add(lib.loans.size());
            out.add(lib.checkoutCounts);
            return out;
        }, List.of("LibraryError: Unknown book", "LibraryError: No copies available", "LibraryError: Loan limit reached", 3,
                Map.of("222", 1, "111", 1, "333", 1)));
        Checker.check("L2-2 returnBook fees", () -> {
            Library lib = sampleLibrary();
            lib.checkout("111", "aarav", "2026-11-01");
            lib.checkout("222", "diya", "2026-11-01");
            int onTime = lib.returnBook("111", "aarav", "2026-11-15");
            int late = lib.returnBook("222", "diya", "2026-11-20");
            return List.of(onTime, late, lib.loans.size(), errorOf(() -> lib.returnBook("222", "diya", "2026-11-21")),
                    lib.availableCopies("222"));
        }, List.of(0, 25, 0, "LibraryError: No such loan", 1));
        Checker.check("L2-3 save writes the agreed text lines", () -> {
            Object result = saveAndLoad();
            return result instanceof List<?> list ? list.get(0) : result;
        }, List.of("BOOK|111|Python 101|Guido|2", "BOOK|222|Learning Data|Wes|1", "BOOK|333|Python Tricks|Dan|1",
                "BOOK|444|Cooking Basics|Ana|1", "LOAN|111|aarav|2026-11-01", "LOAN|222|diya|2026-11-02",
                "COUNT|111|1", "COUNT|222|1"));
        Checker.check("L2-3 save / load round trip", () -> {
            Object result = saveAndLoad();
            return result instanceof List<?> list ? list.subList(1, list.size()) : result;
        }, List.of(true, true, true, 1));
        Checker.check("L2-3 load reads a hand-written file (blank lines are skipped)", () -> loadHandWrittenFile(
                "BOOK|111|Dune|Frank Herbert|2\n\nBOOK|222|Emma|Jane Austen|1\nLOAN|111|aarav|2026-11-01\nCOUNT|111|1\n"),
                List.of(List.of("Dune", "Emma"), 1, 25));
        Checker.check("L2-3 load rejects unknown lines", () -> loadHandWrittenFile("BOOK|111|Dune|Frank|1\nHELLO|world\n"),
                "LibraryError: Bad line: HELLO|world");
        Checker.check("L3-1 overdueReport", () -> {
            Library lib = sampleLibrary();
            lib.checkout("111", "aarav", "2026-11-01");
            lib.checkout("222", "diya", "2026-11-10");
            lib.checkout("333", "aarav", "2026-10-20");
            return lib.overdueReport("2026-11-20");
        }, List.of("aarav: Python 101 (5 days late)", "aarav: Python Tricks (17 days late)"));
        Checker.check("L3-1 overdueReport (nothing late)", () -> {
            Library lib = sampleLibrary();
            lib.checkout("111", "aarav", "2026-11-10");
            return lib.overdueReport("2026-11-24");
        }, List.of());
        Checker.check("L3-2 popularBooks", () -> {
            Library lib = sampleLibrary();
            String[][] borrows = {{"111", "a"}, {"111", "b"}, {"222", "a"}, {"333", "c"}, {"333", "d"}};
            for (String[] borrow : borrows) {
                lib.checkout(borrow[0], borrow[1], "2026-11-01");
                lib.returnBook(borrow[0], borrow[1], "2026-11-02");
            }
            return List.of(lib.popularBooks(2), lib.popularBooks(10), lib.popularBooks(0));
        }, List.of(List.of("Python 101", "Python Tricks"), List.of("Python 101", "Python Tricks", "Learning Data"), List.of()));
        Checker.done();
    }
}
// ==== CHECKER-BEGIN (generated by _dev_tools/java_sync.py - do not edit) ====
final class Checker {
    private static int passed = 0, total = 0;

    /** Compare what your code produced with what we expect and print [PASS] / [FAIL]. */
    static void check(String name, java.util.function.Supplier<Object> fn, Object want) {
        Object got;
        boolean good;
        try {
            got = fn.get();
            good = same(got, want);
        } catch (Throwable e) {              // your code crashed: show why instead of stopping
            got = e.getClass().getSimpleName() + ": " + e.getMessage();
            good = false;
        }
        total++;
        if (good) passed++;
        System.out.println("[" + (good ? "PASS" : "FAIL") + "] " + name
                + (good ? "" : "  (got " + show(got) + ", want " + show(want) + ")"));
    }

    /** Everything that run() prints, as one string (new lines normalised to \n). */
    static String printed(Runnable run) {
        java.io.PrintStream old = System.out;
        java.io.ByteArrayOutputStream buf = new java.io.ByteArrayOutputStream();
        System.setOut(new java.io.PrintStream(buf, true, java.nio.charset.StandardCharsets.UTF_8));
        try {
            run.run();
        } finally {
            System.setOut(old);
        }
        return buf.toString(java.nio.charset.StandardCharsets.UTF_8).replace("\r\n", "\n");
    }

    /** Run fn while System.in contains text (to test code that uses Scanner). */
    static <T> T withInput(String text, java.util.function.Supplier<T> fn) {
        java.io.InputStream old = System.in;
        System.setIn(new java.io.ByteArrayInputStream(text.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        try {
            return fn.get();
        } finally {
            System.setIn(old);
        }
    }

    /** Print the final score line (the portal reads this). */
    static void done() {
        System.out.println("\nScore: " + passed + "/" + total + " checks passed");
    }

    private static boolean same(Object got, Object want) {
        if (got instanceof Number g && want instanceof Number w) {
            boolean floating = got instanceof Double || got instanceof Float || want instanceof Double || want instanceof Float;
            return floating ? Math.abs(g.doubleValue() - w.doubleValue()) < 1e-6 : g.longValue() == w.longValue();
        }
        return java.util.Objects.deepEquals(got, want);
    }

    private static String show(Object o) {
        if (o == null) return "null";
        if (o instanceof String s) {
            return "\"" + s.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t").replace("\"", "\\\"") + "\"";
        }
        if (o instanceof Object[] a) return java.util.Arrays.deepToString(a);
        if (o instanceof int[] a) return java.util.Arrays.toString(a);
        if (o instanceof long[] a) return java.util.Arrays.toString(a);
        if (o instanceof double[] a) return java.util.Arrays.toString(a);
        if (o instanceof char[] a) return java.util.Arrays.toString(a);
        if (o instanceof boolean[] a) return java.util.Arrays.toString(a);
        return String.valueOf(o);
    }
}
// ==== CHECKER-END ====
