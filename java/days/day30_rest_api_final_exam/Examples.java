/* Day 30 - Code along: a tiny REST API with the JDK's built-in HttpServer, called with HttpClient.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * The program starts its own server on a free port of THIS computer (127.0.0.1), calls it, and stops it. No internet needed.
 *
 * To keep it running and open it in a browser, replace the `server.stop(0)` line by `System.in.read();`
 * and visit http://127.0.0.1:<port>/health (the port is printed).
 */
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.*;

class Examples {
    record Product(int id, String name, double price) {}

    static final List<Product> PRODUCTS = new ArrayList<>(List.of(
            new Product(1, "Pen", 10.0), new Product(2, "Notebook", 55.5), new Product(3, "Backpack", 799.0)));

    public static void main(String[] args) throws Exception {
        // ---- 1. Start a server: port 0 = "any free port", 127.0.0.1 = only this computer ----
        HttpServer server = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0);
        server.createContext("/health", exchange -> send(exchange, 200, "{\"status\":\"ok\"}"));
        server.createContext("/products", Examples::products);       // one handler for /products and /products/{id}
        server.start();
        int port = server.getAddress().getPort();
        System.out.println("server is listening on a free port: " + (port > 0));

        try {
            HttpClient client = HttpClient.newHttpClient();
            String base = "http://127.0.0.1:" + port;

            // ---- 2. GET: ask for data ----
            System.out.println(show(client, "GET", base + "/health", null));            // 200 {"status":"ok"}
            System.out.println(show(client, "GET", base + "/products", null));
            System.out.println(show(client, "GET", base + "/products?min_price=50", null));   // query parameter

            // ---- 3. Path parameter and 404 ----
            System.out.println(show(client, "GET", base + "/products/2", null));
            System.out.println(show(client, "GET", base + "/products/99", null));       // 404: no such product

            // ---- 4. POST: send a JSON body, get 201 Created (or 422 for bad data) ----
            System.out.println(show(client, "POST", base + "/products", "{\"name\":\"Eraser\",\"price\":5}"));
            System.out.println(show(client, "POST", base + "/products", "{\"name\":\"\",\"price\":-1}"));
            System.out.println(show(client, "GET", base + "/products", null));          // the new product is there

            // ---- 5. Unknown route and wrong method ----
            System.out.println(show(client, "GET", base + "/nothing-here", null));      // 404 from the server itself
            System.out.println(show(client, "DELETE", base + "/products/1", null));     // 405: we do not allow DELETE
        } finally {
            server.stop(0);                                                              // always stop the server
        }
        System.out.println("server stopped");
    }

    // The handler: decide by method and path, then answer with status + JSON text.
    static void products(com.sun.net.httpserver.HttpExchange exchange) throws IOException {
        String method = exchange.getRequestMethod();
        String path = exchange.getRequestURI().getPath();              // "/products" or "/products/2"
        String query = exchange.getRequestURI().getQuery();            // "min_price=50" or null
        if (path.equals("/products") && method.equals("GET")) {
            double min = query != null && query.startsWith("min_price=") ? Double.parseDouble(query.substring(10)) : 0;
            StringJoiner list = new StringJoiner(",", "[", "]");
            for (Product p : PRODUCTS) {
                if (p.price() >= min) {
                    list.add(json(p));
                }
            }
            send(exchange, 200, list.toString());
        } else if (path.startsWith("/products/") && method.equals("GET")) {
            int id = Integer.parseInt(path.substring("/products/".length()));
            Optional<Product> found = PRODUCTS.stream().filter(p -> p.id() == id).findFirst();
            if (found.isPresent()) {
                send(exchange, 200, json(found.get()));
            } else {
                send(exchange, 404, "{\"error\":\"Product not found\"}");
            }
        } else if (path.equals("/products") && method.equals("POST")) {
            String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            // A real API uses a JSON library; here we pull two values out by hand to keep the example short.
            String name = textValue(body, "name");
            double price = numberValue(body, "price");
            if (name.isBlank() || price <= 0) {
                send(exchange, 422, "{\"error\":\"validation failed\"}");
            } else {
                Product created = new Product(PRODUCTS.size() + 1, name, price);
                PRODUCTS.add(created);
                send(exchange, 201, json(created));
            }
        } else {
            send(exchange, 405, "{\"error\":\"method not allowed\"}");
        }
    }

    static void send(com.sun.net.httpserver.HttpExchange exchange, int status, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);              // status line + headers, then the body
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    static String json(Product p) {
        return "{\"id\":" + p.id() + ",\"name\":\"" + p.name() + "\",\"price\":" + p.price() + "}";
    }

    static String textValue(String body, String key) {
        int start = body.indexOf("\"" + key + "\":\"");
        if (start < 0) {
            return "";
        }
        start += key.length() + 4;
        return body.substring(start, body.indexOf('"', start));
    }

    static double numberValue(String body, String key) {
        int start = body.indexOf("\"" + key + "\":");
        if (start < 0) {
            return 0;
        }
        start += key.length() + 3;
        int end = start;
        while (end < body.length() && "-0123456789.".indexOf(body.charAt(end)) >= 0) {
            end++;
        }
        return Double.parseDouble(body.substring(start, end));
    }

    // The client side: build a request, send it, print "METHOD /path -> status body".
    static String show(HttpClient client, String method, String url, String body) throws Exception {
        HttpRequest.Builder request = HttpRequest.newBuilder(URI.create(url))
                .method(method, body == null ? HttpRequest.BodyPublishers.noBody() : HttpRequest.BodyPublishers.ofString(body));
        HttpResponse<String> response = client.send(request.build(), HttpResponse.BodyHandlers.ofString());
        return method + " " + URI.create(url).getRawPath() + (URI.create(url).getRawQuery() == null ? "" : "?" + URI.create(url).getRawQuery())
                + " -> " + response.statusCode() + " " + response.body();
    }
}
