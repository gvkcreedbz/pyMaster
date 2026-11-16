import java.io.IOException;
import java.io.InterruptedIOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * The PRODUCTION shell around the Watcher: real clock, real internet, a real scheduler thread.
 * NOT used by the demo (the demo ticks by hand on a fake clock). It compiles with everything else, so the
 * example is always checked by javac, but nothing here runs unless you start {@code java -cp out Production}.
 *
 * <p>Python's {@code run_forever(w, sleep, clock)} was a {@code while True} loop. In Java the idiomatic version
 * hands the loop to a {@link ScheduledExecutorService}.
 */
public final class Production {

    private static final Logger LOG = Logger.getLogger("watcher");

    private Production() { }

    /**
     * Call {@code watcher.tick()} every {@code period}, one run after the previous one has finished.
     *
     * <p>GOTCHA: if a scheduled task throws, the executor silently CANCELS all future runs. That is why the task
     * body catches everything: a service that stops checking and says nothing is the worst kind of monitor.
     */
    public static ScheduledExecutorService start(Watcher watcher, Duration period) {
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "watcher-tick");
            t.setDaemon(false);                                  // keep the JVM alive while we are watching
            return t;
        });
        scheduler.scheduleWithFixedDelay(() -> {
            try {
                int ran = watcher.tick();
                LOG.fine(() -> ran + " check(s) ran");
            } catch (RuntimeException e) {                       // e.g. disk full: log it, try again next time
                LOG.log(Level.SEVERE, "tick failed", e);
            }
        }, 0, period.toMillis(), TimeUnit.MILLISECONDS);
        return scheduler;
    }

    /** The real network: java.net.http.HttpClient with a timeout, a clear User-Agent, and 5xx treated as failure. */
    public static Fetcher httpFetcher() {
        HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
        return url -> {
            HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                    .timeout(Duration.ofSeconds(10))
                    .header("User-Agent", "my-watcher/1.0")
                    .build();
            try {
                HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
                if (resp.statusCode() >= 500) throw new IOException("HTTP " + resp.statusCode());
                return resp.body();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new InterruptedIOException("interrupted");
            }
        };
    }

    public static void main(String[] args) {
        List<Target> targets = List.of(
                Target.price("laptop-price", "https://shop.example/laptop", "Price: \\$([\\d,\\.]+)", Duration.ofMinutes(5), 5),
                Target.uptime("payments-api", "https://pay.example/health", Duration.ofMinutes(2)));
        Watcher watcher = new Watcher(targets, httpFetcher(), List.of(new Notifier.Console()),
                Path.of("state.json"), Clock.systemUTC());
        ScheduledExecutorService scheduler = start(watcher, Duration.ofSeconds(5));
        Runtime.getRuntime().addShutdownHook(new Thread(scheduler::shutdown));      // Ctrl+C stops it cleanly
    }
}
