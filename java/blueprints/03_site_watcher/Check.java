/**
 * A plugin: one kind of check. It receives the target and the network, and returns a {@link Reading}
 * or throws. Being a functional interface, a plugin can be a lambda or a method reference (Day 22).
 */
@FunctionalInterface
public interface Check {
    Reading run(Target target, Fetcher fetch) throws Exception;
}
