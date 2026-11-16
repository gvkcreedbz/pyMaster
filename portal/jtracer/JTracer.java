/* JTracer - step-by-step execution recorder for a learner's Java program (the Java twin of tracer_harness.py).
 *
 * Run (from the learner's work directory):
 *     java --add-modules jdk.jdi portal\jtracer\JTracer.java <Target.java> <max_steps> <result.json> [stdin-file]
 *
 * It compiles the target with `javac -g`, launches it in a child JVM through JDI (suspended), single-steps
 * the learner's own classes line by line and writes the same JSON shape as tracer_harness.py:
 *   {"steps":[{line, ev, stack:[{name, vars:{n: enc}}], out, heap, ret?, err?}], "error": null|{type,msg,line},
 *    "output": "<stdout, last 6000 chars>", "truncated": bool, "total_steps": int}
 * enc = {"p": "<inline text>", "k": "<kind>"}  or  {"ref": <heap id>}
 * heap[id] = {"k":"array|list|set","items":[enc..],"more":n} | {"k":"dict","items":[[k,v]..],"more":n}
 *          | {"k":"object","cls":"Name","attrs":{field: enc}}
 * Env: JTRACER_TIMEOUT_MS = wall-clock limit for the child program (default 8000).
 */
import com.sun.jdi.*;
import com.sun.jdi.connect.Connector;
import com.sun.jdi.connect.LaunchingConnector;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;

import javax.tools.*;
import java.io.*;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.charset.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

public class JTracer {
    static final int MAX_ITEMS = 24, MAX_DEPTH = 4, MAX_HEAP = 60;
    static final String[] JDK_EXCLUDES = {"java.*", "javax.*", "jdk.*", "sun.*", "com.sun.*"};
    static final Set<String> BOXES = Set.of("java.lang.Integer", "java.lang.Long", "java.lang.Double", "java.lang.Float",
            "java.lang.Short", "java.lang.Byte", "java.lang.Boolean", "java.lang.Character");
    static final Set<String> NOISE = Set.of();

    // ---- result state -------------------------------------------------------------------------------------
    static final List<Object> steps = new ArrayList<>();
    static boolean truncated;
    static Map<String, Object> error;
    static int maxSteps;
    static long deadline;
    static long timeoutMs = 8000;
    static int lastLine = -1;

    // ---- session state --------------------------------------------------------------------------------------
    static VirtualMachine vm;
    static Process proc;
    static Collector outC, errC;
    static final Set<String> learner = new HashSet<>();
    static ThreadReference mainThread, cur;
    static String srcFileName = "Main.java";
    static boolean done, killed;

    // =====================================================================================================
    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println("usage: java --add-modules jdk.jdi JTracer.java <Target.java> <max_steps> <result.json> [stdin-file]");
            System.exit(2);
        }
        Path target = Path.of(args[0]);
        maxSteps = Integer.parseInt(args[1]);
        Path result = Path.of(args[2]);
        Path stdinFile = args.length > 3 && !args[3].isBlank() ? Path.of(args[3]) : null;
        String env = System.getenv("JTRACER_TIMEOUT_MS");
        if (env != null) {
            try { timeoutMs = Long.parseLong(env.trim()); } catch (NumberFormatException ignored) { }
        }
        Path tmp = null;
        try {
            tmp = Files.createTempDirectory("jtrace");
            run(target, stdinFile, tmp);
        } catch (Throwable t) {
            if (error == null) error = err("TracerError", String.valueOf(t), null);
        } finally {
            shutdown();
            if (tmp != null) deleteTree(tmp);
        }
        Map<String, Object> res = new LinkedHashMap<>();
        res.put("steps", steps);
        res.put("error", error);
        String output = outC == null ? "" : outC.tail(6000);
        res.put("output", output);
        res.put("truncated", truncated);
        res.put("total_steps", steps.size());
        StringBuilder sb = new StringBuilder();
        json(res, sb);
        try {
            Files.writeString(result, sb.toString(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.err.println("cannot write result: " + e);
            System.exit(3);
        }
        System.exit(0);
    }

    // =====================================================================================================
    static void run(Path target, Path stdinFile, Path tmp) throws Exception {
        String src = new String(Files.readAllBytes(target), StandardCharsets.UTF_8);
        if (src.startsWith("\uFEFF")) src = src.substring(1);
        Matcher pm = Pattern.compile("(?m)^\\s*public\\s+(?:(?:final|abstract|sealed|non-sealed|strictfp)\\s+)*"
                + "(?:class|interface|enum|record)\\s+(\\w+)").matcher(src);
        String base;
        if (pm.find()) base = pm.group(1);
        else {
            base = target.getFileName().toString().replaceFirst("\\.java$", "").replaceAll("\\W", "_");
            if (base.isEmpty() || Character.isDigit(base.charAt(0))) base = "Main_" + base;
        }
        srcFileName = base + ".java";
        Path srcDir = Files.createDirectories(tmp.resolve("src"));
        Path outDir = Files.createDirectories(tmp.resolve("out"));
        Path srcFile = srcDir.resolve(srcFileName);
        Files.writeString(srcFile, src, StandardCharsets.UTF_8);

        // ---- (a) compile ------------------------------------------------------------------------------------
        JavaCompiler jc = ToolProvider.getSystemJavaCompiler();
        if (jc == null) { error = err("TracerError", "no Java compiler available (need a JDK)", null); return; }
        DiagnosticCollector<JavaFileObject> dc = new DiagnosticCollector<>();
        boolean ok;
        try (StandardJavaFileManager fm = jc.getStandardFileManager(dc, Locale.ENGLISH, StandardCharsets.UTF_8)) {
            ok = jc.getTask(new StringWriter(), fm, dc,
                    List.of("-g", "-encoding", "UTF-8", "-proc:none", "-nowarn", "-Xlint:none", "-cp", outDir.toString(),
                            "-d", outDir.toString()),
                    null, fm.getJavaFileObjects(srcFile)).call();
        }
        if (!ok) {
            for (Diagnostic<? extends JavaFileObject> d : dc.getDiagnostics()) {
                if (d.getKind() == Diagnostic.Kind.ERROR) {
                    String msg = String.valueOf(d.getMessage(Locale.ENGLISH)).replaceAll("\\s*\\R\\s*", " | ");
                    error = err("CompileError", cut(msg, 300), d.getLineNumber() > 0 ? (int) d.getLineNumber() : null);
                    return;
                }
            }
            error = err("CompileError", "compilation failed", null);
            return;
        }
        try (var walk = Files.walk(outDir)) {
            for (Path p : (Iterable<Path>) walk::iterator) {
                String n = p.getFileName().toString();
                if (n.endsWith(".class")) {
                    String rel = outDir.relativize(p).toString().replace('\\', '.').replace('/', '.');
                    learner.add(rel.substring(0, rel.length() - 6));
                }
            }
        }
        String mainClass = findMain(outDir, src);
        if (mainClass == null) {
            error = err("NoMainMethod", "no 'public static void main(String[] args)' found", null);
            return;
        }

        // ---- (b) launch the child JVM through JDI --------------------------------------------------------------
        LaunchingConnector lc = Bootstrap.virtualMachineManager().defaultConnector();
        Map<String, Connector.Argument> ca = lc.defaultArguments();
        ca.get("main").setValue(mainClass);
        ca.get("options").setValue("-cp \"" + outDir + "\" -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 "
                + "-Dfile.encoding=UTF-8 -Xshare:auto -XX:+UseSerialGC -XX:TieredStopAtLevel=1");
        ca.get("suspend").setValue("true");
        vm = lc.launch(ca);
        proc = vm.process();
        outC = new Collector(proc.getInputStream());
        errC = new Collector(proc.getErrorStream());
        OutputStream pin = proc.getOutputStream();
        if (stdinFile != null && Files.isRegularFile(stdinFile)) {
            byte[] data = Files.readAllBytes(stdinFile);
            Thread w = new Thread(() -> {
                try (OutputStream o = pin) { o.write(data); o.flush(); } catch (IOException ignored) { }
            });
            w.setDaemon(true);
            w.start();
        } else {
            try { pin.close(); } catch (IOException ignored) { }
        }

        EventRequestManager erm = vm.eventRequestManager();
        ClassPrepareRequest cpr = erm.createClassPrepareRequest();
        cpr.addClassFilter(mainClass);
        cpr.setSuspendPolicy(EventRequest.SUSPEND_ALL);
        cpr.enable();
        deadline = System.nanoTime() + timeoutMs * 1_000_000L;
        // Start the VM by resuming the initial VMStart event set (the only suspension at this point). A bare vm.resume()
        // here could race with that set and later let the main class run before our breakpoint exists.
        EventSet first = vm.eventQueue().remove(15000);
        if (first == null) vm.resume(); else first.resume();
        try {
            eventLoop();
        } catch (VMDisconnectedException ignored) { }
    }

    /** First top-level class (in source order) that has a public static void main(String[]). */
    static String findMain(Path outDir, String src) throws Exception {
        List<String> tops = new ArrayList<>();
        for (String n : learner) if (n.indexOf('$') < 0) tops.add(n);
        Map<String, Integer> pos = new HashMap<>();
        for (String n : tops) {
            String simple = n.substring(n.lastIndexOf('.') + 1);
            Matcher m = Pattern.compile("\\b(?:class|record|interface|enum)\\s+" + Pattern.quote(simple) + "\\b").matcher(src);
            pos.put(n, m.find() ? m.start() : Integer.MAX_VALUE);
        }
        tops.sort(Comparator.comparingInt(pos::get));
        try (URLClassLoader cl = new URLClassLoader(new URL[]{outDir.toUri().toURL()}, ClassLoader.getPlatformClassLoader())) {
            for (String n : tops) {
                try {
                    Class<?> c = Class.forName(n, false, cl);
                    java.lang.reflect.Method m = c.getDeclaredMethod("main", String[].class);
                    int mod = m.getModifiers();
                    if (java.lang.reflect.Modifier.isStatic(mod) && java.lang.reflect.Modifier.isPublic(mod)) return n;
                } catch (Throwable ignored) { }
            }
        }
        return null;
    }

    // =====================================================================================================
    // JDI event loop
    // =====================================================================================================
    static void eventLoop() throws Exception {
        EventQueue q = vm.eventQueue();
        while (!done) {
            EventSet set = q.remove(100);
            if (set == null) {
                if (System.nanoTime() > deadline) { timeout(); break; }
                if (!proc.isAlive()) break;
                continue;
            }
            boolean needStep = false;
            boolean hasStep = false;
            for (Event ev : set) if (ev instanceof StepEvent) hasStep = true;
            try {
                for (Event ev : set) {
                    if (ev instanceof VMDeathEvent || ev instanceof VMDisconnectEvent) { done = true; continue; }
                    if (done) continue;
                    if (ev instanceof ClassPrepareEvent cp) {
                        onClassPrepare(cp);
                    } else if (ev instanceof BreakpointEvent be) {
                        mainThread = be.thread();
                        vm.eventRequestManager().deleteEventRequest(be.request());
                        startTracing(mainThread);
                        record("line", be.location().lineNumber(), mainThread, null, null);
                        needStep = true;
                    } else if (ev instanceof StepEvent se) {
                        vm.eventRequestManager().deleteEventRequest(se.request());
                        if (!se.thread().equals(mainThread)) continue;
                        Location l = se.location();
                        if (learner.contains(l.declaringType().name())) {
                            if (l.lineNumber() > 0) record("line", l.lineNumber(), mainThread, null, null);
                            needStep = true;
                        } else {
                            needStep = false;
                            newStep(mainThread, StepRequest.STEP_OUT);
                        }
                    } else if (ev instanceof MethodEntryEvent mee) {
                        // learner code called back from the JDK (lambda in forEach, comparator, ...): the running
                        // step is filtered out inside the JDK, so (re)start stepping here.
                        if (!hasStep && mee.thread().equals(mainThread) && enteredFromJdk(mee)) {
                            record("line", mee.location().lineNumber(), mainThread, null, null);
                            needStep = true;
                        }
                    } else if (ev instanceof MethodExitEvent me) {
                        onMethodExit(me);
                    } else if (ev instanceof ExceptionEvent xe) {
                        onException(xe);
                    }
                    if (done) break;
                }
                if (needStep && !done) newStep(mainThread, StepRequest.STEP_INTO);
                // (entry events above may have left an old step request around; newStep replaces it)
            } catch (VMDisconnectedException e) {
                done = true;
            } catch (RuntimeException e) {
                if (!done) {
                    error = err("TracerError", String.valueOf(e), null);
                    done = true;
                    kill();
                }
            } finally {
                try { set.resume(); } catch (VMDisconnectedException ignored) { }
            }
            if (!done && System.nanoTime() > deadline) { timeout(); break; }
        }
    }

    static void timeout() {
        truncated = true;
        error = err("TimeoutError", "Stopped after " + (timeoutMs / 1000.0) + "s. Is there a loop that never ends?",
                lastLine > 0 ? lastLine : null);
        kill();
        done = true;
    }

    static void kill() {
        killed = true;
        if (proc != null) proc.destroyForcibly();
    }

    static void onClassPrepare(ClassPrepareEvent cp) {
        EventRequestManager erm = vm.eventRequestManager();
        erm.deleteEventRequest(cp.request());
        ReferenceType rt = cp.referenceType();
        List<Method> ms = rt.methodsByName("main", "([Ljava/lang/String;)V");
        if (ms.isEmpty()) return;
        BreakpointRequest br = erm.createBreakpointRequest(ms.get(0).location());
        br.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        br.enable();
    }

    static void startTracing(ThreadReference t) {
        EventRequestManager erm = vm.eventRequestManager();
        MethodEntryRequest me = erm.createMethodEntryRequest();
        me.addThreadFilter(t);
        for (String x : JDK_EXCLUDES) me.addClassExclusionFilter(x);
        me.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        me.enable();
        MethodExitRequest mx = erm.createMethodExitRequest();
        mx.addThreadFilter(t);
        for (String x : JDK_EXCLUDES) mx.addClassExclusionFilter(x);
        mx.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        mx.enable();
        ExceptionRequest xr = erm.createExceptionRequest(null, true, true);
        xr.addThreadFilter(t);
        xr.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        xr.enable();
    }

    static boolean enteredFromJdk(MethodEntryEvent e) {
        try {
            Method m = e.method();
            if (!learner.contains(m.declaringType().name()) || e.location().lineNumber() < 0) return false;
            ThreadReference t = e.thread();
            if (t.frameCount() < 2) return false;
            return !learner.contains(t.frame(1).location().declaringType().name());
        } catch (IncompatibleThreadStateException | IndexOutOfBoundsException ex) {
            return false;
        }
    }

    static void newStep(ThreadReference t, int depth) {
        EventRequestManager erm = vm.eventRequestManager();
        for (StepRequest old : new ArrayList<>(erm.stepRequests())) {
            if (old.thread().equals(t)) erm.deleteEventRequest(old);
        }
        StepRequest sr = erm.createStepRequest(t, StepRequest.STEP_LINE, depth);
        for (String x : JDK_EXCLUDES) sr.addClassExclusionFilter(x);
        sr.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
        sr.enable();
    }

    static void onMethodExit(MethodExitEvent me) {
        Method m = me.method();
        if (!learner.contains(m.declaringType().name())) return;
        int line = me.location().lineNumber();
        if (line < 0) return;
        Value rv = null;
        try { rv = me.returnValue(); } catch (UnsupportedOperationException ignored) { }
        record("return", line, me.thread(), rv == null ? vm.mirrorOfVoid() : rv, null);
    }

    static void onException(ExceptionEvent xe) throws Exception {
        ThreadReference th = xe.thread();
        if (!th.equals(mainThread)) return;
        Location tl = xe.location(), cl = xe.catchLocation();
        boolean uncaught = cl == null;
        boolean ok = learner.contains(tl.declaringType().name()) || uncaught
                || learner.contains(cl.declaringType().name());
        if (!ok) return;
        int line = innermostLearnerLine(th);
        if (line < 0) return;
        cur = th;
        ObjectReference ex = xe.exception();
        String type = errType(ex.referenceType().name());
        String msg = exMessage(ex);
        if (uncaught) error = err(type, cut(msg == null ? "" : msg, 300), line);
        record("exception", line, th, null, type + (msg == null || msg.isEmpty() ? "" : ": " + msg));
    }

    static int innermostLearnerLine(ThreadReference th) throws Exception {
        for (StackFrame f : th.frames(0, Math.min(th.frameCount(), 400))) {
            Location l = f.location();
            if (learner.contains(l.declaringType().name())) return l.lineNumber();
        }
        return -1;
    }

    static String exMessage(ObjectReference ex) {
        try {
            if (isJdk(ex.referenceType().name())) {
                Value v = invoke(ex, "getMessage", "()Ljava/lang/String;");
                if (v instanceof StringReference s) return s.value();
                return null;
            }
            Value v = fv(ex, "java.lang.Throwable", "detailMessage");
            if (v instanceof StringReference s) return s.value();
        } catch (Exception ignored) { }
        return null;
    }

    // =====================================================================================================
    // recording one step
    // =====================================================================================================
    static void record(String ev, int line, ThreadReference th, Value ret, String errText) {
        if (steps.size() >= maxSteps) {
            truncated = true;
            done = true;
            kill();
            return;
        }
        cur = th;
        Map<Long, Object> heap = new LinkedHashMap<>();
        Map<String, Object> rec = new LinkedHashMap<>();
        rec.put("line", line);
        rec.put("ev", ev);
        rec.put("stack", snapshot(th, heap));
        outC.sync();
        rec.put("out", outC.total);
        if (ev.equals("return")) rec.put("ret", ret == null ? prim("void", "void") : enc(ret, heap, 0));
        if (errText != null) rec.put("err", errText);
        rec.put("heap", heap);
        steps.add(rec);
        lastLine = line;
    }

    static List<Object> snapshot(ThreadReference th, Map<Long, Object> heap) {
        List<Object> stack = new ArrayList<>();
        try {
            List<StackFrame> frames = th.frames(0, Math.min(th.frameCount(), 400));
            for (int i = frames.size() - 1; i >= 0; i--) {
                StackFrame sf = frames.get(i);
                Location loc = sf.location();
                if (!learner.contains(loc.declaringType().name())) continue;
                Map<String, Object> vars = new LinkedHashMap<>();
                try {
                    ObjectReference self = sf.thisObject();
                    if (self != null && !loc.method().isStaticInitializer()) vars.put("this", enc(self, heap, 0));
                } catch (RuntimeException ignored) { }
                List<LocalVariable> lv;
                try { lv = sf.visibleVariables(); } catch (AbsentInformationException e) { lv = List.of(); }
                Map<LocalVariable, Value> vals = sf.getValues(lv);
                for (LocalVariable v : lv) {
                    if (v.name().indexOf('$') >= 0) continue;
                    vars.put(v.name(), enc(vals.get(v), heap, 0));
                }
                Map<String, Object> fr = new LinkedHashMap<>();
                fr.put("name", frameName(loc.method()));
                fr.put("vars", vars);
                stack.add(fr);
            }
        } catch (VMDisconnectedException e) {
            throw e;
        } catch (Exception ignored) { }
        return stack;
    }

    static String frameName(Method m) {
        String n = m.name();
        if (n.equals("<init>")) return simple(m.declaringType().name()) + "()";
        if (n.equals("<clinit>")) return "static init";
        if (n.startsWith("lambda$")) return "lambda()";
        return n + "()";
    }

    // =====================================================================================================
    // value encoding
    // =====================================================================================================
    static Map<String, Object> prim(String p, String k) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("p", p);
        m.put("k", k);
        return m;
    }

    static Map<String, Object> ref(long id) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("ref", id);
        return m;
    }

    static String simple(String cn) {
        int i = cn.lastIndexOf('.');
        return (i >= 0 ? cn.substring(i + 1) : cn).replace('$', '.');
    }

    static String errType(String cn) {
        int i = Math.max(cn.lastIndexOf('.'), cn.lastIndexOf('$'));
        return i >= 0 ? cn.substring(i + 1) : cn;
    }

    static boolean isJdk(String cn) {
        return cn.startsWith("java.") || cn.startsWith("javax.") || cn.startsWith("jdk.") || cn.startsWith("sun.")
                || cn.startsWith("com.sun.");
    }

    static String quote(String s, char q, int limit) {
        if (s.length() > limit) s = s.substring(0, limit - 3) + "...";
        StringBuilder sb = new StringBuilder().append(q);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c == q) sb.append('\\').append(c);
                    else sb.append(c);
                }
            }
        }
        return sb.append(q).toString();
    }

    static Map<String, Object> enc(Value v, Map<Long, Object> heap, int depth) {
        try {
            return enc0(v, heap, depth);
        } catch (VMDisconnectedException e) {
            throw e;
        } catch (Exception e) {
            return prim("?", "error");
        }
    }

    static Map<String, Object> enc0(Value v, Map<Long, Object> heap, int depth) throws Exception {
        if (v == null) return prim("null", "null");
        if (v instanceof BooleanValue b) return prim(String.valueOf(b.value()), "boolean");
        if (v instanceof CharValue c) return prim(quote(String.valueOf(c.value()), '\'', 10), "char");
        if (v instanceof IntegerValue i) return prim(String.valueOf(i.value()), "int");
        if (v instanceof LongValue l) return prim(String.valueOf(l.value()), "long");
        if (v instanceof ShortValue s) return prim(String.valueOf(s.value()), "short");
        if (v instanceof ByteValue b) return prim(String.valueOf(b.value()), "byte");
        if (v instanceof FloatValue f) return prim(Float.toString(f.value()), "float");
        if (v instanceof DoubleValue d) return prim(Double.toString(d.value()), "double");
        if (v instanceof VoidValue) return prim("void", "void");
        if (!(v instanceof ObjectReference o)) return prim(String.valueOf(v), "?");
        if (o instanceof StringReference s) return prim(quote(s.value(), '"', 60), "String");

        ReferenceType rt = o.referenceType();
        String cn = rt.name();
        if (o instanceof ArrayReference ar) {
            long id = o.uniqueID();
            if (heap.containsKey(id)) return ref(id);
            if (depth > MAX_DEPTH || heap.size() > MAX_HEAP) return prim("...", simple(cn));
            int len = ar.length();
            Map<String, Object> box = heapBox(heap, id, "array", Math.max(0, len - MAX_ITEMS));
            List<Object> items = new ArrayList<>();
            box.put("items", items);
            if (len > 0) for (Value x : ar.getValues(0, Math.min(len, MAX_ITEMS))) items.add(enc(x, heap, depth + 1));
            return ref(id);
        }
        String c = cat(rt);
        switch (c) {
            case "box": {
                Map<String, Object> inner = enc(fv(o, cn, "value"), heap, depth);
                return prim(String.valueOf(inner.get("p")), simple(cn));
            }
            case "enum": {
                Value n = fv(o, "java.lang.Enum", "name");
                return prim(n instanceof StringReference s ? s.value() : simple(cn), "enum");
            }
            case "lambda": return prim("lambda", "func");
            case "class": return prim("class " + simple(((ClassObjectReference) o).reflectedType().name()), "func");
            case "sb": {
                Value s = invoke(o, "toString", "()Ljava/lang/String;");
                return prim(s instanceof StringReference sr ? quote(sr.value(), '"', 60) : "?", simple(cn));
            }
            case "throwable": {
                String m = exMessage(o);
                return prim(errType(cn) + (m == null || m.isEmpty() ? "" : ": " + cut(m, 50)), "exception");
            }
            case "tostring": {
                Value s = invoke(o, "toString", "()Ljava/lang/String;");
                return prim(s instanceof StringReference sr ? cut(sr.value(), 60) : simple(cn), simple(cn));
            }
            case "jdk": return prim(simple(cn), simple(cn));
            default: break;
        }
        long id = o.uniqueID();
        if (heap.containsKey(id)) return ref(id);
        if (depth > MAX_DEPTH || heap.size() > MAX_HEAP) return prim("...", simple(cn));

        if (c.equals("list") || c.equals("set")) {
            Items it = readSeq(o);
            if (it == null) return prim(simple(cn), simple(cn));
            Map<String, Object> box = heapBox(heap, id, c, Math.max(0, it.total - MAX_ITEMS));
            List<Object> items = new ArrayList<>();
            box.put("items", items);
            for (Value x : it.vals) items.add(enc(x, heap, depth + 1));
            return ref(id);
        }
        if (c.equals("dict")) {
            Items it = readMap(o);
            if (it == null) return prim(simple(cn), simple(cn));
            Map<String, Object> box = heapBox(heap, id, "dict", Math.max(0, it.total - MAX_ITEMS));
            List<Object> items = new ArrayList<>();
            box.put("items", items);
            for (Value[] kv : it.pairs) items.add(List.of(enc(kv[0], heap, depth + 1), enc(kv[1], heap, depth + 1)));
            return ref(id);
        }
        // user object
        Map<String, Object> box = new LinkedHashMap<>();
        box.put("k", "object");
        box.put("cls", simple(cn));
        Map<String, Object> attrs = new LinkedHashMap<>();
        box.put("attrs", attrs);
        heap.put(id, box);
        List<Field> fl = new ArrayList<>();
        for (Field f : rt.visibleFields()) {
            if (f.isStatic() || f.isSynthetic() || isJdk(f.declaringType().name())) continue;
            if (fl.size() < MAX_ITEMS) fl.add(f);
        }
        if (!fl.isEmpty()) {
            Map<Field, Value> vals = o.getValues(fl);
            for (Field f : fl) attrs.put(f.name(), enc(vals.get(f), heap, depth + 1));
        }
        return ref(id);
    }

    static Map<String, Object> heapBox(Map<Long, Object> heap, long id, String kind, int more) {
        Map<String, Object> box = new LinkedHashMap<>();
        box.put("k", kind);
        box.put("items", new ArrayList<>());
        box.put("more", more);
        heap.put(id, box);
        return box;
    }

    // ---- type categories (cached per class name) ----------------------------------------------------------
    static final Map<String, String> CAT = new HashMap<>();
    static final Map<String, Field> FIELDS = new HashMap<>();

    static boolean isA(ReferenceType rt, String target) {
        if (rt.name().equals(target)) return true;
        if (rt instanceof ClassType ct) {
            for (InterfaceType it : ct.allInterfaces()) if (it.name().equals(target)) return true;
            for (ClassType s = ct.superclass(); s != null; s = s.superclass()) if (s.name().equals(target)) return true;
        }
        return false;
    }

    /** The JDK collection implementation we can read cheaply through its fields, or null. */
    static String fast(ReferenceType rt) {
        for (ReferenceType t = rt; t != null; t = t instanceof ClassType ct ? ct.superclass() : null) {
            switch (t.name()) {
                case "java.util.ArrayList", "java.util.LinkedHashMap", "java.util.HashMap", "java.util.LinkedHashSet",
                        "java.util.HashSet" -> { return t.name(); }
                default -> { }
            }
        }
        return null;
    }

    static String cat(ReferenceType rt) {
        String cn = rt.name();
        String c = CAT.get(cn);
        if (c != null) return c;
        boolean jdk = isJdk(cn);
        boolean readable = jdk || fast(rt) != null;
        if (BOXES.contains(cn)) c = "box";
        else if (isA(rt, "java.lang.Enum")) c = "enum";
        else if (cn.contains("$$Lambda")) c = "lambda";
        else if (cn.equals("java.lang.Class")) c = "class";
        else if (cn.equals("java.lang.StringBuilder") || cn.equals("java.lang.StringBuffer")) c = "sb";
        else if (isA(rt, "java.util.Map")) c = readable ? "dict" : "object";
        else if (isA(rt, "java.util.Set")) c = readable ? "set" : "object";
        else if (isA(rt, "java.util.Collection")) c = readable ? "list" : "object";
        else if (isA(rt, "java.lang.Throwable")) c = "throwable";
        else if (!jdk) c = "object";
        else if (cn.startsWith("java.math.") || cn.startsWith("java.time.") || cn.startsWith("java.util.Optional")
                || cn.startsWith("java.util.concurrent.atomic.") || cn.equals("java.util.UUID")) c = "tostring";
        else c = "jdk";
        CAT.put(cn, c);
        return c;
    }

    // ---- reading JDK collections -----------------------------------------------------------------------------
    static final class Items {
        List<Value> vals = new ArrayList<>();
        List<Value[]> pairs = new ArrayList<>();
        int total;
    }

    static Value fv(ObjectReference o, String decl, String name) {
        ReferenceType rt = o.referenceType();
        String key = rt.name() + "#" + decl + "." + name;
        Field f = FIELDS.get(key);
        if (f == null) {
            for (Field x : rt.allFields()) {
                if (x.name().equals(name) && x.declaringType().name().equals(decl)) { f = x; break; }
            }
            if (f == null) throw new IllegalStateException("no field " + key);
            FIELDS.put(key, f);
        }
        return o.getValue(f);
    }

    static int intf(ObjectReference o, String decl, String name) {
        return ((IntegerValue) fv(o, decl, name)).value();
    }

    static Value invoke(ObjectReference o, String name, String sig) throws Exception {
        if (cur == null) throw new IllegalStateException("no thread");
        Method pick = null;
        for (Method m : o.referenceType().methodsByName(name, sig)) {
            if (!m.isAbstract()) { pick = m; break; }
            if (pick == null) pick = m;
        }
        if (pick == null) throw new IllegalStateException("no method " + name);
        return o.invokeMethod(cur, pick, Collections.emptyList(), ObjectReference.INVOKE_SINGLE_THREADED);
    }

    static Items readSeq(ObjectReference o) throws Exception {
        String fk = fast(o.referenceType());
        Items it = new Items();
        if ("java.util.ArrayList".equals(fk)) {
            int size = intf(o, "java.util.ArrayList", "size");
            it.total = size;
            Value ed = fv(o, "java.util.ArrayList", "elementData");
            if (ed instanceof ArrayReference ar && size > 0) it.vals = new ArrayList<>(ar.getValues(0, Math.min(size, MAX_ITEMS)));
            return it;
        }
        if ("java.util.HashSet".equals(fk) || "java.util.LinkedHashSet".equals(fk)) {
            Value m = fv(o, "java.util.HashSet", "map");
            Items mi = readMap((ObjectReference) m);
            if (mi == null) return null;
            it.total = mi.total;
            for (Value[] p : mi.pairs) it.vals.add(p[0]);
            return it;
        }
        if (isJdk(o.referenceType().name())) return viaToArray(o);
        return null;
    }

    static Items viaToArray(ObjectReference o) throws Exception {
        Value r = invoke(o, "toArray", "()[Ljava/lang/Object;");
        if (!(r instanceof ArrayReference ar)) return null;
        Items it = new Items();
        try {
            ar.disableCollection();
            it.total = ar.length();
            int n = Math.min(it.total, MAX_ITEMS);
            if (n > 0) it.vals = new ArrayList<>(ar.getValues(0, n));
        } finally {
            try { ar.enableCollection(); } catch (RuntimeException ignored) { }
        }
        return it;
    }

    static Items readMap(ObjectReference o) throws Exception {
        String fk = fast(o.referenceType());
        Items it = new Items();
        if ("java.util.LinkedHashMap".equals(fk) || "java.util.HashMap".equals(fk)) {
            it.total = intf(o, "java.util.HashMap", "size");
            final String NODE = "java.util.HashMap$Node";
            if ("java.util.LinkedHashMap".equals(fk)) {
                ObjectReference e = fv(o, "java.util.LinkedHashMap", "head") instanceof ObjectReference r ? r : null;
                int guard = 0;
                while (e != null && it.pairs.size() < MAX_ITEMS && guard++ < 100000) {
                    it.pairs.add(new Value[]{fv(e, NODE, "key"), fv(e, NODE, "value")});
                    e = fv(e, "java.util.LinkedHashMap$Entry", "after") instanceof ObjectReference r ? r : null;
                }
            } else if (fv(o, "java.util.HashMap", "table") instanceof ArrayReference tab) {
                int len = Math.min(tab.length(), 8192);
                List<Value> buckets = len > 0 ? tab.getValues(0, len) : List.of();
                for (Value b : buckets) {
                    ObjectReference e = b instanceof ObjectReference r ? r : null;
                    int guard = 0;
                    while (e != null && it.pairs.size() < MAX_ITEMS && guard++ < 10000) {
                        it.pairs.add(new Value[]{fv(e, NODE, "key"), fv(e, NODE, "value")});
                        e = fv(e, NODE, "next") instanceof ObjectReference r ? r : null;
                    }
                    if (it.pairs.size() >= MAX_ITEMS) break;
                }
            }
            return it;
        }
        if (!isJdk(o.referenceType().name())) return null;
        Value es = invoke(o, "entrySet", "()Ljava/util/Set;");
        if (!(es instanceof ObjectReference eso)) return null;
        Items ei = viaToArray(eso);
        if (ei == null) return null;
        it.total = ei.total;
        for (Value e : ei.vals) {
            ObjectReference er = (ObjectReference) e;
            it.pairs.add(new Value[]{invoke(er, "getKey", "()Ljava/lang/Object;"), invoke(er, "getValue", "()Ljava/lang/Object;")});
        }
        return it;
    }

    // =====================================================================================================
    // captured child output
    // =====================================================================================================
    static final class Collector implements Runnable {
        final InputStream in;
        final StringBuilder sb = new StringBuilder();
        long total;
        boolean pendingCR;
        byte[] carry = new byte[0];
        final CharsetDecoder dec = StandardCharsets.UTF_8.newDecoder()
                .onMalformedInput(CodingErrorAction.REPLACE).onUnmappableCharacter(CodingErrorAction.REPLACE);
        volatile boolean stop;
        final Thread th;

        Collector(InputStream in) {
            this.in = in;
            th = new Thread(this, "collector");
            th.setDaemon(true);
            th.start();
        }

        public void run() {
            while (!stop) {
                drain();
                try { Thread.sleep(2); } catch (InterruptedException e) { return; }
            }
        }

        synchronized void drain() {
            try {
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.available()) > 0) {
                    int r = in.read(buf, 0, Math.min(n, buf.length));
                    if (r < 0) break;
                    feed(buf, r);
                }
            } catch (IOException ignored) { }
        }

        void sync() { drain(); }

        synchronized void feed(byte[] b, int n) {
            ByteBuffer bb = ByteBuffer.allocate(carry.length + n);
            bb.put(carry).put(b, 0, n).flip();
            CharBuffer cb = CharBuffer.allocate(bb.remaining() + 4);
            dec.decode(bb, cb, false);
            cb.flip();
            carry = new byte[bb.remaining()];
            bb.get(carry);
            while (cb.hasRemaining()) {
                char c = cb.get();
                if (pendingCR) {
                    pendingCR = false;
                    if (c != '\n') { sb.append('\r'); total++; }
                }
                if (c == '\r') { pendingCR = true; continue; }
                sb.append(c);
                total++;
            }
            if (sb.length() > 1_500_000) sb.delete(0, 500_000);
        }

        void finish() {
            stop = true;
            try { th.join(500); } catch (InterruptedException ignored) { }
            synchronized (this) {
                try {
                    byte[] buf = new byte[8192];
                    int r;
                    while ((r = in.read(buf)) >= 0) feed(buf, r);
                } catch (IOException ignored) { }
                if (pendingCR) { sb.append('\r'); total++; pendingCR = false; }
            }
        }

        synchronized String tail(int n) {
            return sb.length() <= n ? sb.toString() : sb.substring(sb.length() - n);
        }
    }

    // =====================================================================================================
    // shutdown / helpers
    // =====================================================================================================
    static void shutdown() {
        try {
            if (proc != null) {
                if (!killed && !proc.waitFor(3, java.util.concurrent.TimeUnit.SECONDS)) kill();
                if (killed) proc.waitFor(3, java.util.concurrent.TimeUnit.SECONDS);
            }
        } catch (InterruptedException ignored) { }
        if (vm != null) {
            try { vm.dispose(); } catch (Throwable ignored) { }
        }
        if (outC != null) outC.finish();
        if (errC != null) errC.finish();
        if (error == null && !truncated && errC != null) stderrFallback();
    }

    /** Failures that happened outside our event hooks (e.g. an exception in a static initializer). */
    static void stderrFallback() {
        String se = errC.tail(4000);
        Matcher m = Pattern.compile("Exception in thread \"[^\"]*\" ([\\w.$]+)(?::[ ]?([^\\r\\n]*))?").matcher(se);
        if (m.find()) {
            Integer line = null;
            Matcher lm = Pattern.compile("\\(" + Pattern.quote(srcFileName) + ":(\\d+)\\)").matcher(se);
            if (lm.find()) line = Integer.parseInt(lm.group(1));
            error = err(errType(m.group(1)), cut(m.group(2) == null ? "" : m.group(2), 300), line);
        } else if (steps.isEmpty() && proc != null && !proc.isAlive() && proc.exitValue() != 0 && !se.isBlank()) {
            error = err("TracerError", cut(se.strip(), 400), null);
        }
    }

    static Map<String, Object> err(String type, String msg, Integer line) {
        Map<String, Object> e = new LinkedHashMap<>();
        e.put("type", type);
        e.put("msg", msg);
        e.put("line", line);
        return e;
    }

    static String cut(String s, int n) {
        return s.length() <= n ? s : s.substring(0, n);
    }

    static void deleteTree(Path p) {
        try (var walk = Files.walk(p)) {
            List<Path> all = new ArrayList<>();
            walk.forEach(all::add);
            Collections.reverse(all);
            for (Path x : all) {
                try { Files.deleteIfExists(x); } catch (IOException ignored) { }
            }
        } catch (IOException ignored) { }
    }

    // ---- minimal JSON writer -------------------------------------------------------------------------------
    static void json(Object o, StringBuilder sb) {
        if (o == null) sb.append("null");
        else if (o instanceof String s) jstr(s, sb);
        else if (o instanceof Boolean || o instanceof Number) sb.append(o);
        else if (o instanceof Map<?, ?> m) {
            sb.append('{');
            boolean first = true;
            for (Map.Entry<?, ?> e : m.entrySet()) {
                if (!first) sb.append(',');
                first = false;
                jstr(String.valueOf(e.getKey()), sb);
                sb.append(':');
                json(e.getValue(), sb);
            }
            sb.append('}');
        } else if (o instanceof Iterable<?> it) {
            sb.append('[');
            boolean first = true;
            for (Object x : it) {
                if (!first) sb.append(',');
                first = false;
                json(x, sb);
            }
            sb.append(']');
        } else jstr(String.valueOf(o), sb);
    }

    static void jstr(String s, StringBuilder sb) {
        sb.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                case '\b' -> sb.append("\\b");
                case '\f' -> sb.append("\\f");
                default -> {
                    if (c < 0x20 || (Character.isSurrogate(c) && !validSurrogate(s, i))) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
                }
            }
        }
        sb.append('"');
    }

    static boolean validSurrogate(String s, int i) {
        char c = s.charAt(i);
        if (Character.isHighSurrogate(c)) return i + 1 < s.length() && Character.isLowSurrogate(s.charAt(i + 1));
        return i > 0 && Character.isHighSurrogate(s.charAt(i - 1));
    }
}
