import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.function.Function;

/**
 * Runs the triage pipeline end to end on a messy sample file, with a deliberately flaky fake AI.
 * Run:  javac -d out *.java   then   java -cp out Demo      (JDK 21 only, no network, no real sleeping, deterministic)
 */
public class Demo {

    static final String SAMPLE = """
            id,received,customer,text
            1,2026-11-16 09:01,  asha  ,"My card was charged TWICE for order 5521!!"
            2,2026-11-16 09:04,ravi,"App   crashes when I open settings on Android"
            3,2026-11-16 09:09,meera,"I can't log in, my account is locked"
            4,2026-11-16 09:15,john,"It would be nice if you could add dark mode"
            5,2026-11-16 09:20,sara,"Hello, is the store open on Sunday?"
            6,2026-11-16 09:22,lee,"Please send a refund for the January invoice"
            6,2026-11-16 09:22,lee,"(duplicate row from a double export)"
            x,2026-11-16 09:30,bad,"This row has a broken id"
            8,2026-11-16 09:31,ghost,"   "
            9,2026-11-16 09:40,kim,"Your delivery estimate widget feels slow and confusing"
            """;

    static void say(String line) { System.out.print(line + "\n"); }          // "\n" always: same bytes on every OS

    static String f(String pattern, Object... args) { return String.format(Locale.ROOT, pattern, args); }

    /** Pretend model: 503 on its 1st and 3rd call, answers in prose once, otherwise returns JSON. */
    static Function<String, String> flakyAi() {
        int[] calls = {0};                                                    // a one-slot array: lambdas need effectively-final
        return prompt -> {
            calls[0]++;
            String text = prompt.substring(prompt.indexOf("\n\n") + 2).toLowerCase(Locale.ROOT);
            if (calls[0] == 1 || calls[0] == 3) throw new Pipeline.TransientException("503 service unavailable");
            if (text.contains("store open")) return "Sure! I would say this is a general question.";   // not JSON
            if (text.contains("slow")) return "{\"label\": \"bug\", \"confidence\": 0.82}";
            return "{\"label\": \"other\", \"confidence\": 0.9}";
        };
    }

    static String clip(String s, int max) { return s.length() <= max ? s : s.substring(0, max); }

    public static void main(String[] args) {
        Pipeline.TicketStore store = new Pipeline.TicketStore();
        List<Double> waits = new ArrayList<>();                               // record the backoff instead of really sleeping

        say("== 0. the chain (a sealed interface: the compiler knows every classifier)");
        say("  " + Pipeline.describe(new Pipeline.RuleClassifier()));
        say("  llm  -> " + Pipeline.describe(new Pipeline.LLMClassifier(p -> "", new Pipeline.Stats(), s -> { }, new Random(0))));

        say("\n== 1. cleaning (lazy streams: nothing is read until the stream is consumed)");
        Pipeline.Stats peek = new Pipeline.Stats();
        var lazy = Pipeline.clean(Pipeline.readRows(SAMPLE), peek);
        say("  stream built, rows read so far: " + peek.get("rows_in"));
        long good = lazy.count();
        say("  stream consumed, rows read: " + peek.get("rows_in") + ", clean tickets: " + good);

        Pipeline.Result run1 = Pipeline.run(SAMPLE, store, flakyAi(), waits::add, new Random(42));
        Pipeline.Stats stats = run1.stats();
        say("  " + stats.startingWith("rows", "rejected"));

        say("\n== 2. who decided each ticket (cheap rules first, AI only when unsure)");
        for (Pipeline.Ticket t : store.all()) {
            say(f("  #%-2d %-6s %-8s by %-7s %-6s %s", t.id(), t.customer(), t.label(), t.source(), t.priority(), clip(t.text(), 44)));
        }

        say("\n== 3. resilience");
        say("  AI calls made: " + stats.get("llm_calls") + " | retried after backoff: " + waits.size()
                + " | AI failures handled: " + stats.get("llm_failed"));
        say("  backoff waits (s): " + waits.stream().map(w -> f("%.2f", w)).toList());

        say("\n== 4. the report");
        say(run1.report().toJson());

        say("\n== 5. run the same file again: nothing duplicates (idempotent upsert)");
        List<Pipeline.Ticket> before = store.all();
        Pipeline.Result run2 = Pipeline.run(SAMPLE, store, flakyAi(), s -> { }, new Random(42));
        say("  total before: " + run1.report().total() + " | total after: " + run2.report().total());
        say("  rows identical after the second run: " + before.equals(store.all()));
        say("  AI calls in run 1: " + stats.get("llm_calls") + " | AI calls in run 2: " + run2.stats().get("llm_calls"));

        say("\n== 6. priorities are a pure function (no store, no network, no clock)");
        say("  urgent ticket ids: " + run2.report().urgentIds());
        Pipeline.Ticket probe = Pipeline.Ticket.raw(100, "Test", "Please fix ASAP, checkout is down", "");
        say("  priorityOf(\"" + probe.text() + "\") = " + Pipeline.priorityOf(probe));
        say("  priorityOf(\"dark mode please\")      = "
                + Pipeline.priorityOf(Pipeline.Ticket.raw(101, "Test", "dark mode please", "")));
    }
}
