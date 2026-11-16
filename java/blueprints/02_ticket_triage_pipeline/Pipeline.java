import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.Set;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.TreeMap;
import java.util.HashSet;
import java.util.function.DoubleConsumer;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

/**
 * Support-ticket triage pipeline: the shape of most data / AI back-ends.
 *
 *   CSV text -> clean -> classify (cheap rules first, AI only when unsure, safe default last) -> store -> report
 *
 * Java 21, JDK only. The real AI call is an injected Function&lt;String,String&gt; you can swap (see LLMClassifier).
 * Everything lives in ONE file as static nested types so the portal can run:  javac -d out *.java ; java -cp out Demo
 */
public final class Pipeline {

    private Pipeline() { }

    public static final List<String> LABELS = List.of("billing", "bug", "account", "feature", "other");

    // ---- 1. DATA SHAPE: records instead of loose maps (immutable, equals/hashCode/toString for free) -----------------
    public record Ticket(int id, String customer, String text, String received,
                         String label, double confidence, String source, String priority) {

        static Ticket raw(int id, String customer, String text, String received) {
            return new Ticket(id, customer, text, received, null, 0.0, "", "normal");
        }

        Ticket decided(String newLabel, double newConfidence, String newSource) {
            return new Ticket(id, customer, text, received, newLabel, newConfidence, newSource, priority);
        }

        Ticket withPriority(String newPriority) {
            return new Ticket(id, customer, text, received, label, confidence, source, newPriority);
        }
    }

    /** What a classifier answers. The compact constructor is "validation at the edge": a bad score cannot exist. */
    public record Decision(String label, double confidence) {
        public Decision {
            if (label == null || !LABELS.contains(label)) {
                throw new IllegalArgumentException("unknown label '" + label + "'");
            }
            if (Double.isNaN(confidence) || confidence < 0.0 || confidence > 1.0) {
                throw new IllegalArgumentException("confidence out of range: " + confidence);
            }
        }
    }

    /** The Python Counter: every stage can bump a named number. TreeMap keeps the printout sorted and deterministic. */
    public static final class Stats {
        private final Map<String, Integer> counts = new TreeMap<>();

        public void bump(String key) { counts.merge(key, 1, Integer::sum); }
        public void set(String key, int value) { counts.put(key, value); }
        public int get(String key) { return counts.getOrDefault(key, 0); }
        public Map<String, Integer> asMap() { return java.util.Collections.unmodifiableMap(new TreeMap<>(counts)); }

        /** Sorted view of the counters whose name starts with one of the prefixes. */
        public Map<String, Integer> startingWith(String... prefixes) {
            return counts.entrySet().stream()
                    .filter(e -> Stream.of(prefixes).anyMatch(e.getKey()::startsWith))
                    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (a, b) -> a, TreeMap::new));
        }
    }

    // ---- 2. PIPELINE STAGES AS LAZY STREAMS: rows flow through one at a time, memory stays flat ---------------------
    /** A tiny CSV reader (the JDK has none). Handles quotes, escaped quotes, commas and newlines inside quotes. */
    static Iterator<List<String>> csvRecords(String text) {
        return new Iterator<>() {
            private int pos = 0;

            @Override public boolean hasNext() { return pos < text.length(); }

            @Override public List<String> next() {
                List<String> fields = new ArrayList<>();
                StringBuilder cur = new StringBuilder();
                boolean quoted = false;
                while (pos < text.length()) {
                    char c = text.charAt(pos++);
                    if (quoted) {
                        if (c == '"') {
                            if (pos < text.length() && text.charAt(pos) == '"') { cur.append('"'); pos++; }
                            else quoted = false;
                        } else {
                            cur.append(c);
                        }
                    } else if (c == '"') {
                        quoted = true;
                    } else if (c == ',') {
                        fields.add(cur.toString());
                        cur.setLength(0);
                    } else if (c == '\n') {
                        break;
                    } else if (c != '\r') {
                        cur.append(c);
                    }
                }
                fields.add(cur.toString());
                return fields;
            }
        };
    }

    /** CSV text -> a LAZY stream of header-keyed rows. Nothing is parsed until a terminal operation pulls on it. */
    public static Stream<Map<String, String>> readRows(String csvText) {
        Iterator<List<String>> it = csvRecords(csvText);
        if (!it.hasNext()) return Stream.empty();
        List<String> header = it.next().stream().map(String::strip).toList();
        return StreamSupport.stream(Spliterators.spliteratorUnknownSize(it, Spliterator.ORDERED), false)
                .filter(rec -> !(rec.size() == 1 && rec.get(0).isBlank()))          // like DictReader: skip blank lines
                .map(rec -> {
                    Map<String, String> row = new LinkedHashMap<>();
                    for (int i = 0; i < header.size(); i++) row.put(header.get(i), i < rec.size() ? rec.get(i) : null);
                    return row;
                });
    }

    /** "  asha  " -> "Asha" (Python's str.title()). */
    static String title(String s) {
        StringBuilder out = new StringBuilder();
        boolean startOfWord = true;
        for (char c : s.toCharArray()) {
            out.append(startOfWord ? Character.toUpperCase(c) : Character.toLowerCase(c));
            startOfWord = !Character.isLetter(c);
        }
        return out.toString();
    }

    /** Trim, dedupe, reject. Each rejected row bumps a counter; each good row becomes a Ticket. */
    public static Stream<Ticket> clean(Stream<Map<String, String>> rows, Stats stats) {
        Set<Integer> seen = new HashSet<>();                       // state lives in the stage; fine for a sequential stream
        return rows.map(row -> cleanOne(row, stats, seen)).flatMap(Optional::stream);
    }

    private static Optional<Ticket> cleanOne(Map<String, String> row, Stats stats, Set<Integer> seen) {
        stats.bump("rows_in");
        int id;
        try {
            id = Integer.parseInt(Optional.ofNullable(row.get("id")).orElse("").strip());
        } catch (NumberFormatException e) {
            stats.bump("rejected_bad_id");
            return Optional.empty();
        }
        String text = Optional.ofNullable(row.get("text")).orElse("").replaceAll("\\s+", " ").strip();
        if (text.isEmpty()) {
            stats.bump("rejected_empty");
            return Optional.empty();
        }
        if (!seen.add(id)) {                                       // the same ticket exported twice: keep the first
            stats.bump("rejected_duplicate");
            return Optional.empty();
        }
        String customer = title(Optional.ofNullable(row.get("customer")).orElse("").strip());
        String received = Optional.ofNullable(row.get("received")).orElse("").strip();
        return Optional.of(Ticket.raw(id, customer, text, received));
    }

    // ---- 3. STRATEGY: a sealed interface = a closed, compiler-checked list of classifiers -----------------------------
    public sealed interface Classifier permits RuleClassifier, LLMClassifier {
        String name();
        Decision classify(String text);
    }

    /** Free, instant, explainable. Handles the obvious 70% so the expensive model only sees the hard 30%. */
    public static final class RuleClassifier implements Classifier {
        private static final Map<String, Pattern> RULES = new LinkedHashMap<>();
        static {
            RULES.put("billing", Pattern.compile("charg|refund|invoice|payment|\\bcard\\b|billed"));
            RULES.put("bug", Pattern.compile("crash|error|broken|not working|fails?\\b|\\bbug\\b"));
            RULES.put("account", Pattern.compile("password|log ?in|locked|2fa|sign ?in"));
            RULES.put("feature", Pattern.compile("wish|would be nice|please add|feature request|could you add"));
        }

        @Override public String name() { return "rules"; }

        @Override public Decision classify(String text) {
            String low = text.toLowerCase(Locale.ROOT);
            String best = "other";
            int bestHits = 0;
            for (Map.Entry<String, Pattern> rule : RULES.entrySet()) {       // first label wins a tie, like Python's max()
                int hits = 0;
                Matcher m = rule.getValue().matcher(low);
                while (m.find()) hits++;
                if (hits > bestHits) { best = rule.getKey(); bestHits = hits; }
            }
            return bestHits == 0 ? new Decision("other", 0.2) : new Decision(best, Math.min(0.55 + 0.2 * bestHits, 0.95));
        }
    }

    // ---- 4. RETRY with exponential backoff + jitter. Sleeper and Random are INJECTED, so tests are instant ------------
    /** Timeouts, 429s, 503s: worth trying again. An IllegalArgumentException is NOT transient: retrying cannot fix it. */
    public static class TransientException extends RuntimeException {
        private static final long serialVersionUID = 1L;

        public TransientException(String message) { super(message); }
    }

    public static <T> T retry(int times, double baseSeconds, DoubleConsumer sleeper, Random rng, Supplier<T> call) {
        for (int attempt = 1; ; attempt++) {
            try {
                return call.get();
            } catch (TransientException e) {
                if (attempt >= times) throw e;
                // 0.2s, 0.4s, 0.8s ... plus up to one "base" of jitter
                sleeper.accept(baseSeconds * Math.pow(2, attempt - 1) + rng.nextDouble() * baseSeconds);
            }
        }
    }

    /** The production sleeper. Tests and the demo pass something else (a recorder, or a no-op). */
    public static final DoubleConsumer REAL_SLEEPER = seconds -> {
        try {
            Thread.sleep((long) (seconds * 1000));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    };

    // ---- 5. ADAPTER: hides one vendor's API behind our Classifier interface -------------------------------------------
    /** `client` is any Function(prompt) -> reply. In production it wraps OpenAI / Anthropic / a local model. */
    public static final class LLMClassifier implements Classifier {
        private static final Pattern LABEL = Pattern.compile("\"label\"\\s*:\\s*\"([^\"]*)\"");
        private static final Pattern CONF = Pattern.compile("\"confidence\"\\s*:\\s*(-?[0-9]*\\.?[0-9]+)");

        private final Function<String, String> client;
        private final Stats stats;
        private final DoubleConsumer sleeper;
        private final Random rng;

        public LLMClassifier(Function<String, String> client, Stats stats, DoubleConsumer sleeper, Random rng) {
            this.client = client;
            this.stats = stats;
            this.sleeper = sleeper;
            this.rng = rng;
        }

        @Override public String name() { return "llm"; }

        private String askOnce(String text) {
            stats.bump("llm_calls");
            return client.apply("Classify this support ticket as one of " + String.join("|", LABELS)
                    + ". Reply ONLY with JSON like {\"label\": \"...\", \"confidence\": 0.9}.\n\n" + text);
        }

        @Override public Decision classify(String text) {
            String reply = retry(3, 0.2, sleeper, rng, () -> askOnce(text));
            if (!reply.strip().startsWith("{")) {                  // model replied with prose instead of JSON
                throw new IllegalArgumentException("model did not return JSON");
            }
            Matcher label = LABEL.matcher(reply);
            Matcher conf = CONF.matcher(reply);
            String found = label.find() ? label.group(1) : null;
            double confidence = conf.find() ? Double.parseDouble(conf.group(1)) : 0.5;
            return new Decision(found, confidence);                // never trust a model: the record validates label + score
        }
    }

    /** Exhaustive switch over a sealed type: add a third classifier and this stops compiling until you handle it. */
    public static String describe(Classifier c) {
        return switch (c) {
            case RuleClassifier r -> "rules (free, instant, explainable)";
            case LLMClassifier l -> "llm (slow, costs money, retried, validated)";
        };
    }

    // ---- 6. FALLBACK CHAIN: first confident answer wins, a failure never kills the batch ------------------------------
    public static final class Triage {
        private final List<Classifier> chain;
        private final Stats stats;
        private final double minConfidence;

        public Triage(List<Classifier> chain, Stats stats, double minConfidence) {
            this.chain = List.copyOf(chain);
            this.stats = stats;
            this.minConfidence = minConfidence;
        }

        public Ticket label(Ticket t) {
            Ticket out = null;
            for (Classifier c : chain) {
                try {
                    Decision d = c.classify(t.text());
                    if (d.confidence() >= minConfidence) {
                        out = t.decided(d.label(), d.confidence(), c.name());
                        break;
                    }
                } catch (Exception e) {                            // a batch job must survive one bad ticket
                    stats.bump(c.name() + "_failed");
                }
            }
            if (out == null) out = t.decided("other", 0.0, "default");   // nothing was sure: park it for a human
            out = out.withPriority(priorityOf(out));
            stats.bump("source_" + out.source());
            return out;
        }
    }

    private static final Pattern URGENT =
            Pattern.compile("urgent|asap|twice|locked out|can'?t (log|sign)|charged", Pattern.CASE_INSENSITIVE);

    /** A pure function: same input, same output, trivial to unit-test. */
    public static String priorityOf(Ticket t) {
        boolean urgent = URGENT.matcher(t.text()).find();
        boolean crashingBug = "bug".equals(t.label()) && t.text().toLowerCase(Locale.ROOT).contains("crash");
        return urgent || crashingBug ? "high" : "normal";
    }

    // ---- 7. STORAGE: idempotent upsert keyed by id, so re-running the same file never duplicates anything -------------
    public record Report(int total, Map<String, Long> byLabel, Map<String, Long> decidedBy, List<Integer> urgentIds) {
        /** Pretty JSON by hand (the JDK has no JSON writer), same layout as the Python demo. */
        public String toJson() {
            return "{\n"
                    + "  \"total\": " + total + ",\n"
                    + "  \"by_label\": " + objectJson(byLabel) + ",\n"
                    + "  \"decided_by\": " + objectJson(decidedBy) + ",\n"
                    + "  \"urgent_ids\": " + urgentIds + "\n"
                    + "}";
        }

        private static String objectJson(Map<String, Long> m) {
            return m.entrySet().stream()
                    .map(e -> "    \"" + e.getKey() + "\": " + e.getValue())
                    .collect(Collectors.joining(",\n", "{\n", "\n  }"));
        }
    }

    /** In-memory stand-in for the SQLite table: the "repository" that owns all reads and writes. */
    public static final class TicketStore {
        private final Map<Integer, Ticket> rows = new TreeMap<>();

        /** Insert, or on a key clash update only the decision columns (SQL: ON CONFLICT(id) DO UPDATE ...). */
        public int upsert(Stream<Ticket> tickets) {
            int[] written = {0};                                   // forEach (not peek+count): count() may skip the pipeline
            tickets.forEach(t -> {
                rows.merge(t.id(), t, (old, neu) ->
                        new Ticket(old.id(), old.customer(), old.text(), old.received(),
                                neu.label(), neu.confidence(), neu.source(), neu.priority()));
                written[0]++;
            });
            return written[0];
        }

        public List<Ticket> all() { return List.copyOf(rows.values()); }
        public int size() { return rows.size(); }

        public Report report() {
            Map<String, Long> byLabel = rows.values().stream()
                    .collect(Collectors.groupingBy(Ticket::label, Collectors.counting()))
                    .entrySet().stream()
                    .sorted(Map.Entry.<String, Long>comparingByValue(Comparator.reverseOrder()).thenComparing(Map.Entry.comparingByKey()))
                    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (a, b) -> a, LinkedHashMap::new));
            Map<String, Long> bySource = rows.values().stream()
                    .collect(Collectors.groupingBy(Ticket::source, TreeMap::new, Collectors.counting()));
            List<Integer> urgent = rows.values().stream()
                    .filter(t -> t.priority().equals("high")).map(Ticket::id).sorted().toList();
            return new Report(rows.size(), byLabel, bySource, urgent);
        }
    }

    // ---- 8. THE WHOLE JOB: a few lines that read like the diagram ---------------------------------------------------
    public record Result(Report report, Stats stats) { }

    /** `ai` may be null (rules only). `sleeper` and `rng` are injected so the job is instant and deterministic in tests. */
    public static Result run(String csvText, TicketStore store, Function<String, String> ai,
                             DoubleConsumer sleeper, Random rng) {
        Stats stats = new Stats();
        List<Classifier> chain = new ArrayList<>();
        chain.add(new RuleClassifier());
        if (ai != null) chain.add(new LLMClassifier(ai, stats, sleeper, rng));
        Triage triage = new Triage(chain, stats, 0.7);
        int stored = store.upsert(clean(readRows(csvText), stats).map(triage::label));   // the terminal op pulls every row through
        stats.set("stored", stored);
        return new Result(store.report(), stats);
    }
}
