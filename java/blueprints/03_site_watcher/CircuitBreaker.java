import java.time.Clock;
import java.time.Duration;
import java.time.Instant;

/**
 * 2. CIRCUIT BREAKER: stop hammering something that is clearly down.
 *
 * <pre>
 *   CLOSED --(max failures in a row)--> OPEN --(cool-off elapsed)--> HALF_OPEN
 *      ^                                  ^                             |
 *      |                                  +------ probe fails ----------+
 *      +------------------------- probe succeeds -----------------------+
 * </pre>
 *
 * Python inferred "half-open" from a timestamp; Java makes it a real, named state (an enum, Day 20).
 * Time comes from an INJECTED {@link Clock}: tests give it a fake one and "wait" five minutes in zero milliseconds.
 */
public final class CircuitBreaker {

    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final int maxFailures;
    private final Duration coolOff;
    private final Clock clock;

    private State state = State.CLOSED;
    private int failures;
    private Instant openedAt;

    public CircuitBreaker(int maxFailures, Duration coolOff, Clock clock) {
        this.maxFailures = maxFailures;
        this.coolOff = coolOff;
        this.clock = clock;
    }

    /**
     * May the caller try the real call now? While OPEN the answer is no until the cool-off has elapsed;
     * then the breaker moves to HALF_OPEN and lets a probe through. The watcher makes one call per tick and
     * records its result straight away, so exactly one probe is in flight.
     */
    public boolean allow() {
        return switch (state) {
            case CLOSED, HALF_OPEN -> true;
            case OPEN -> {
                boolean coolOffOver = !clock.instant().isBefore(openedAt.plus(coolOff));
                if (coolOffOver) state = State.HALF_OPEN;
                yield coolOffOver;
            }
        };
    }

    /** Report the result of a call. A failed probe re-opens immediately; a success closes the breaker. */
    public void record(boolean ok) {
        if (ok) {
            failures = 0;
            openedAt = null;
            state = State.CLOSED;
            return;
        }
        failures++;
        if (state == State.HALF_OPEN || failures >= maxFailures) {
            state = State.OPEN;
            openedAt = clock.instant();           // (re)open: stay quiet for coolOff
        }
    }

    public State state() {
        return state;
    }

    public int failures() {
        return failures;
    }
}
