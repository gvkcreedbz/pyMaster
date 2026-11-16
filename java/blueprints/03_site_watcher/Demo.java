import java.io.IOException;
import java.net.SocketTimeoutException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.stream.Stream;

/**
 * Simulates 40 minutes of watching three sites in a few milliseconds, using a fake clock and a fake internet.
 * Run:  javac -d out *.java   then   java -cp out Demo      (JDK only, no real sleeping, no real network)
 */
public class Demo {

    private static final Instant START = Instant.parse("2026-01-01T00:00:00Z");

    private static final Target LAPTOP = Target.price("laptop-price", "https://shop.example/laptop",
            "Price: \\$([\\d,\\.]+)", Duration.ofSeconds(300), 5);

    private static final List<Target> TARGETS = List.of(
            LAPTOP,
            Target.content("docs-page", "https://docs.example/changelog", Duration.ofSeconds(600)),
            Target.uptime("payments-api", "https://pay.example/health", Duration.ofSeconds(120)));

    /** A clock we can move by hand. java.time.Clock is abstract, so a test double is three small methods. */
    static final class FakeClock extends Clock {
        private Instant now;

        FakeClock(Instant start) {
            this.now = start;
        }

        void set(Instant instant) {
            this.now = instant;
        }

        @Override public ZoneId getZone() { return ZoneOffset.UTC; }
        @Override public Clock withZone(ZoneId zone) { return this; }
        @Override public Instant instant() { return now; }
    }

    /** A pretend web whose pages change as the fake clock moves. */
    static final class FakeInternet {
        private final Clock clock;
        int calls;

        FakeInternet(Clock clock) {
            this.clock = clock;
        }

        String fetch(String url) throws IOException {
            calls++;
            double minute = Duration.between(START, clock.instant()).toSeconds() / 60.0;
            if (url.contains("shop.example")) {
                int price = minute < 10 ? 1299 : minute < 20 ? 1099 : 1089;        // -15% at minute 10, tiny -1% at minute 20
                return String.format(Locale.US, "<html>Laptop Pro   Price: $%,.2f  In stock</html>", (double) price);
            }
            if (url.contains("docs.example")) {
                return minute < 25 ? "<h1>Changelog</h1> v1.0" : "<h1>Changelog</h1> v1.1 released";
            }
            if (url.contains("pay.example")) {
                if (minute >= 12 && minute < 28) throw new SocketTimeoutException("connection timed out");   // outage 12..28
                return "ok";
            }
            throw new IllegalArgumentException(url);
        }
    }

    public static void main(String[] args) throws Exception {
        Path tmp = Files.createTempDirectory("watcher-demo");
        try {
            run(tmp);
        } finally {
            deleteTree(tmp);
        }
        System.out.println("\n== 7. cleanup");
        System.out.println("   temp folder removed: " + !Files.exists(tmp));
    }

    private static void run(Path tmp) throws IOException {
        FakeClock clock = new FakeClock(START);
        FakeInternet net = new FakeInternet(clock);
        Notifier.Console notifier = new Notifier.Console();
        Path stateFile = Files.createDirectory(tmp.resolve("main")).resolve("state.json");
        Watcher w = new Watcher(TARGETS, net::fetch, List.of(notifier), stateFile, clock);

        System.out.println("== 0. plugins registered in the registry: " + Checks.kinds());

        System.out.println("\n== 1. forty minutes pass, one tick per minute (fake clock)");
        for (int minute = 0; minute <= 40; minute++) {
            clock.set(START.plus(Duration.ofMinutes(minute)));
            int before = notifier.sent().size();
            int ran = w.tick();
            if (notifier.sent().size() > before) {
                System.out.printf("   (minute %2d: %d check(s) ran)%n", minute, ran);
            }
        }

        System.out.println("\n== 2. what the dashboard would show");
        w.status().forEach((name, s) -> System.out.printf("   %-13s last=%-14s breaker=%-9s consecutive failures=%d%n",
                name, s.last(), s.breaker(), s.failures()));

        System.out.println("\n== 3. efficiency: the schedule and the breaker avoid pointless calls");
        System.out.println("   fake HTTP calls: " + net.calls + "  (checking every target every minute would be " + 41 * 3 + ")");

        System.out.println("\n== 4. alerts are transitions, not noise");
        System.out.println("   " + notifier.sent().size() + " alerts in 40 minutes: "
                + notifier.sent().stream().map(Notifier.Alert::title).toList());

        System.out.println("\n== 5. restart the service: it remembers (atomic JSON state file)");
        Watcher w2 = new Watcher(TARGETS, net::fetch, List.of(notifier), stateFile, clock);
        System.out.println("   after restart, laptop-price last seen = "
                + w2.lastSeen("laptop-price").map(Reading::display).orElse("nothing"));

        System.out.println("\n== 6. a layout change is reported as an error, not a wrong price");
        FakeClock otherClock = new FakeClock(START);
        Path brokenState = Files.createDirectory(tmp.resolve("broken")).resolve("s.json");
        Watcher broken = new Watcher(List.of(LAPTOP.withPattern("Cost: \\$([\\d\\.]+)")), net::fetch,
                List.of(notifier), brokenState, otherClock);
        for (int i = 0; i < 3; i++) {
            otherClock.set(START.plusSeconds(i * 1000L));
            broken.tick();
        }
        System.out.println("   status: " + broken.status());
    }

    /** Delete a folder and everything inside it (children first). */
    private static void deleteTree(Path root) throws IOException {
        try (Stream<Path> paths = Files.walk(root)) {
            for (Path p : paths.sorted(Comparator.reverseOrder()).toList()) {
                Files.deleteIfExists(p);
            }
        }
    }
}
