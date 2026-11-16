import java.io.IOException;

/**
 * The INJECTED network: give me a URL, I give you the page text, or I throw (timeout, 5xx, DNS...).
 * Production passes a lambda around java.net.http.HttpClient; the demo passes a fake website (Day 22).
 */
@FunctionalInterface
public interface Fetcher {
    String fetch(String url) throws IOException;
}
