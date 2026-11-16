import java.util.ArrayList;
import java.util.List;

/**
 * 3. OBSERVER: anything with {@code send(title, body)} can receive alerts. In Python this was a
 * {@code typing.Protocol} (structural typing). Java is nominal: a class must say {@code implements Notifier}.
 * Because it has ONE abstract method, a lambda also works: {@code (title, body) -> System.out.println(title)}.
 */
@FunctionalInterface
public interface Notifier {

    void send(String title, String body) throws Exception;

    /** One alert, remembered by {@link Console} so tests can look at it. A record is perfect for a plain data carrier. */
    record Alert(String title, String body) { }

    /** Prints alerts and keeps a copy. */
    final class Console implements Notifier {
        private final List<Alert> sent = new ArrayList<>();

        @Override
        public void send(String title, String body) {
            sent.add(new Alert(title, body));
            System.out.println("   ALERT  " + title + ": " + body);
        }

        public List<Alert> sent() {
            return List.copyOf(sent);                 // defensive copy: callers cannot change our history
        }
    }

    /** The network call used by {@link Webhook}. Injected (HttpClient in production, a lambda in tests). */
    @FunctionalInterface
    interface Poster {
        void post(String url, String jsonBody) throws Exception;
    }

    /** Slack / Teams / Discord all accept a JSON POST. */
    final class Webhook implements Notifier {
        private final String url;
        private final Poster poster;

        public Webhook(String url, Poster poster) {
            this.url = url;
            this.poster = poster;
        }

        @Override
        public void send(String title, String body) throws Exception {
            String text = "*" + title + "*\n" + body;
            poster.post(url, "{\"text\": \"" + text.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\"}");
        }
    }
}
