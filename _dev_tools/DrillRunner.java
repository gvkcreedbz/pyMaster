import java.io.*;
import java.lang.reflect.*;
import java.net.URI;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import javax.tools.*;

/**
 * Long-lived helper for _dev_tools/verify_drills.py: compiles and runs many small Java programs in ONE JVM
 * (starting a JVM per snippet costs seconds; this costs a few hundred milliseconds).
 *
 * Protocol on stdin/stdout (binary, UTF-8):
 *   request : "RUN <timeoutMs> <codeBytes> <stdinBytes>\n" + code + stdin
 *   response: "RES <exitCode> <outBytes>\n" + combined stdout/stderr text
 * exitCode: 0 ok, 1 uncaught exception or compile error, -9 timed out (the helper exits after answering).
 * Started with: java DrillRunner.java
 */
public class DrillRunner {
    static final Pattern CLS = Pattern.compile("(?m)^\\s*(?:public\\s+|final\\s+|abstract\\s+)*(?:class|interface|enum|record)\\s+(\\w+)");

    static String readLine(InputStream in) throws IOException {
        StringBuilder sb = new StringBuilder();
        int c;
        while ((c = in.read()) != -1 && c != '\n') sb.append((char) c);
        return c == -1 && sb.length() == 0 ? null : sb.toString();
    }

    static byte[] readN(InputStream in, int n) throws IOException {
        byte[] b = in.readNBytes(n);
        if (b.length != n) throw new EOFException();
        return b;
    }

    public static void main(String[] args) throws Exception {
        InputStream in = new BufferedInputStream(System.in);
        OutputStream out = new BufferedOutputStream(new FileOutputStream(FileDescriptor.out));
        InputStream realIn = System.in;
        PrintStream realOut = System.out, realErr = System.err;
        Path root = Files.createTempDirectory("drillrunner");
        int seq = 0;
        String line;
        while ((line = readLine(in)) != null) {
            String[] h = line.trim().split(" ");
            if (h.length != 4 || !h[0].equals("RUN")) continue;
            long timeout = Long.parseLong(h[1]);
            String code = new String(readN(in, Integer.parseInt(h[2])), StandardCharsets.UTF_8);
            byte[] stdin = readN(in, Integer.parseInt(h[3]));
            ByteArrayOutputStream cap = new ByteArrayOutputStream();
            PrintStream ps = new PrintStream(cap, true, StandardCharsets.UTF_8);
            int rc;
            boolean timedOut = false;
            Path dir = root.resolve("c" + (seq++));
            Files.createDirectories(dir);
            try {
                Matcher m = CLS.matcher(code);
                if (!m.find()) throw new IllegalStateException("no class found");
                String cls = m.group(1);
                Path src = dir.resolve("Drill.java");
                Files.writeString(src, code, StandardCharsets.UTF_8);
                JavaCompiler jc = ToolProvider.getSystemJavaCompiler();
                StringWriter diag = new StringWriter();
                int cr = jc.getTask(diag, null, null, List.of("-encoding", "UTF-8", "-proc:none", "-d", dir.toString()),
                        null, jc.getStandardFileManager(null, null, StandardCharsets.UTF_8).getJavaFileObjects(src.toFile())).call() ? 0 : 1;
                if (cr != 0) {
                    ps.print(diag.toString().replace(src.toString(), "Drill.java"));
                    ps.print("error: compilation failed\n");
                    rc = 1;
                } else {
                    System.setIn(new ByteArrayInputStream(stdin));
                    System.setOut(ps);
                    System.setErr(ps);
                    final int[] code2 = {0};
                    URLClassLoader cl = new URLClassLoader(new URL[]{dir.toUri().toURL()}, DrillRunner.class.getClassLoader());
                    Thread t = new Thread(() -> {
                        try {
                            Method main = Class.forName(cls, true, cl).getMethod("main", String[].class);
                            main.invoke(null, (Object) new String[0]);
                        } catch (InvocationTargetException e) {
                            Throwable c = e.getCause();
                            ps.print("Exception in thread \"main\" ");
                            c.printStackTrace(ps);
                            code2[0] = 1;
                        } catch (Throwable e) {
                            e.printStackTrace(ps);
                            code2[0] = 1;
                        }
                    });
                    t.setDaemon(true);
                    t.start();
                    t.join(timeout);
                    timedOut = t.isAlive();
                    rc = timedOut ? -9 : code2[0];
                }
            } catch (Throwable e) {
                ps.print(e + "\n");
                rc = 1;
            } finally {
                System.setIn(realIn);
                System.setOut(realOut);
                System.setErr(realErr);
            }
            ps.flush();
            byte[] res = cap.toByteArray();
            out.write(("RES " + rc + " " + res.length + "\n").getBytes(StandardCharsets.UTF_8));
            out.write(res);
            out.flush();
            if (timedOut) System.exit(0);   // a runaway thread may still be burning CPU: start fresh
        }
    }
}
