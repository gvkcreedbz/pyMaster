import java.io.UncheckedIOException;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Site and price watcher: the skeleton of every automation / monitoring service.
 *
 * <pre>
 *   scheduler tick --> for each due target: circuit breaker? --> Checks plugin --> compare with last state
 *                                                                                       |
 *                                  notifiers (console, webhook, ...)  <-- only when something CHANGED
 * </pre>
 *
 * JDK only. Time (a {@link Clock}) and the network (a {@link Fetcher}) are INJECTED, so the whole service can be
 * tested in milliseconds with a fake clock and a fake website: {@code java -cp out Demo}.
 *
 * <p>Nobody sleeps in here. {@link #tick()} does one round of work and returns; WHO calls it and how often is
 * somebody else's job (see {@code Production} for a ScheduledExecutorService, and {@code Demo} for a fake clock).
 */
public final class Watcher {

    private static final Logger LOG = Logger.getLogger("watcher");

    static final int MAX_FAILURES = 3;
    static final Duration COOL_OFF = Duration.ofMinutes(5);

    private final List<Target> targets;
    private final Fetcher fetch;
    private final List<Notifier> notifiers;
    private final Path statePath;
    private final Clock clock;

    private final Map<String, Reading> state;                                     // last known value of every target
    private final Map<String, CircuitBreaker> breakers = new LinkedHashMap<>();   // insertion order = dashboard order
    private final Map<String, Instant> due = new LinkedHashMap<>();               // when each target may run next

    /** What the dashboard shows for one target. */
    public record Status(String last, CircuitBreaker.State breaker, int failures) { }

    public Watcher(List<Target> targets, Fetcher fetch, List<Notifier> notifiers, Path statePath, Clock clock) {
        this.targets = List.copyOf(targets);
        this.fetch = fetch;
        this.notifiers = List.copyOf(notifiers);
        this.statePath = statePath;
        this.clock = clock;
        this.state = StateStore.load(statePath);                 // survive restarts: remember the last value of every target
    }

    // ---- alerting (observer) --------------------------------------------------------------------------------------

    private void alert(String title, String body) {
        for (Notifier n : notifiers) {
            try {
                n.send(title, body);
            } catch (Exception e) {                              // one broken Slack hook must not stop the rest
                LOG.log(Level.WARNING, "notifier " + n.getClass().getSimpleName() + " failed", e);
            }
        }
    }

    // ---- the heart: one tick ---------------------------------------------------------------------------------------

    /**
     * Run every target that is due right now (according to the injected clock). Returns how many were checked.
     * {@code synchronized} because a status page thread may call {@link #status()} while the scheduler thread ticks.
     */
    public synchronized int tick() {
        Instant now = clock.instant();
        int ran = 0;
        for (Target t : targets) {
            Instant dueAt = due.get(t.name());
            if (dueAt != null && dueAt.isAfter(now)) continue;               // not due yet
            due.put(t.name(), now.plus(t.every()));
            CircuitBreaker br = breakers.computeIfAbsent(t.name(), n -> new CircuitBreaker(MAX_FAILURES, COOL_OFF, clock));
            if (!br.allow()) continue;                                       // OPEN and still cooling off
            ran++;
            Reading value;
            try {
                value = Checks.lookup(t.kind()).run(t, fetch);
            } catch (Exception e) {                                          // fail-soft: one target never stops the others
                CircuitBreaker.State before = br.state();
                br.record(false);
                if (br.state() == CircuitBreaker.State.OPEN && before == CircuitBreaker.State.CLOSED) {
                    // alert on the TRANSITION closed -> open, not on every failed minute
                    alert(t.name() + " is failing", br.failures() + " failures in a row ("
                            + e.getClass().getSimpleName() + ": " + e.getMessage() + "). Pausing checks.");
                }
                continue;
            }
            if (br.state() != CircuitBreaker.State.CLOSED) {                 // OPEN/HALF_OPEN -> CLOSED: the probe worked
                alert(t.name() + " recovered", "the check works again");
            }
            br.record(true);
            compare(t, value);
        }
        try {
            StateStore.save(statePath, state);
        } catch (IOException e) {
            throw new UncheckedIOException("cannot save " + statePath, e);
        }
        return ran;
    }

    private void compare(Target t, Reading value) {
        Reading old = state.put(t.name(), value);
        if (old == null || old.equals(value)) return;                        // first sighting, or nothing changed: stay quiet
        switch (value) {
            case Reading.Price now when old instanceof Reading.Price was && was.value() > 0 -> {
                double drop = (was.value() - now.value()) / was.value() * 100;
                if (drop >= t.minDropPct()) {
                    alert(t.name() + ": price dropped " + String.format(Locale.ROOT, "%.0f", drop) + "%",
                            num(was.value()) + " -> " + num(now.value()) + "  " + t.url());
                }
            }
            default -> alert(t.name() + " changed", old.display() + " -> " + value.display());
        }
    }

    /** Like Python's {:g}: 1299.0 prints as 1299, 12.50 as 12.5. */
    private static String num(double v) {
        return BigDecimal.valueOf(v).stripTrailingZeros().toPlainString();
    }

    // ---- read-only views --------------------------------------------------------------------------------------------

    public synchronized Map<String, Status> status() {
        Map<String, Status> out = new LinkedHashMap<>();
        breakers.forEach((name, b) -> out.put(name,
                new Status(Optional.ofNullable(state.get(name)).map(Reading::display).orElse(null), b.state(), b.failures())));
        return out;
    }

    public synchronized Optional<Reading> lastSeen(String name) {
        return Optional.ofNullable(state.get(name));
    }
}
