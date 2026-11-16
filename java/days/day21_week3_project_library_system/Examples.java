/* Day 21 - Code along: a guided tour of the SAME idea with bikes (a cycle-rental shop).
 *
 * Read it, type it, run it (java Examples.java). Then build your Library in Practice.java.
 * Same shape: records for data, one class that keeps the rules, a custom exception, a text file on disk.
 */
import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;
class Examples {
    static final int FREE_DAYS = 1;          // no magic numbers inside the methods
    static final int FEE_PER_DAY = 50;
    static final int MAX_RENTALS = 2;
    static class RentalError extends RuntimeException {       // our own error type (Day 17)
        RentalError(String message) {
            super(message);
        }
    }
    record Bike(String id, String model, int count) {         // data = record
    }
    record Rental(String bikeId, String customer, String out) {
    }
    static class RentalShop {                                  // rules = class
        private final Map<String, Bike> bikes = new TreeMap<>();
        private final List<Rental> rentals = new ArrayList<>();
        void addBike(Bike bike) {
            Bike stored = bikes.get(bike.id());
            if (stored == null) {
                bikes.put(bike.id(), bike);
            } else {
                bikes.put(bike.id(), new Bike(bike.id(), bike.model(), stored.count() + bike.count()));
            }
        }
        int free(String id) {
            Bike bike = bikes.get(id);
            if (bike == null) {
                return 0;
            }
            int out = 0;
            for (Rental rental : rentals) {
                if (rental.bikeId().equals(id)) {
                    out++;
                }
            }
            return bike.count() - out;
        }
        void rent(String id, String customer, String date) {
            if (!bikes.containsKey(id)) {
                throw new RentalError("Unknown bike");                  // check the rules in a fixed order
            }
            if (free(id) < 1) {
                throw new RentalError("No bike free");
            }
            int held = 0;
            for (Rental rental : rentals) {
                if (rental.customer().equals(customer)) {
                    held++;
                }
            }
            if (held >= MAX_RENTALS) {
                throw new RentalError("Rental limit reached");
            }
            rentals.add(new Rental(id, customer, date));
        }
        int giveBack(String id, String customer, String date) {
            for (Rental rental : rentals) {
                if (rental.bikeId().equals(id) && rental.customer().equals(customer)) {
                    rentals.remove(rental);
                    long days = ChronoUnit.DAYS.between(LocalDate.parse(rental.out()), LocalDate.parse(date));
                    return (int) Math.max(0, days - FREE_DAYS) * FEE_PER_DAY;
                }
            }
            throw new RentalError("No such rental");
        }
        // persistence = one text line per fact
        void save(Path path) throws IOException {
            List<String> lines = new ArrayList<>();
            for (Bike bike : bikes.values()) {
                lines.add("BIKE|" + bike.id() + "|" + bike.model() + "|" + bike.count());
            }
            for (Rental rental : rentals) {
                lines.add("RENT|" + rental.bikeId() + "|" + rental.customer() + "|" + rental.out());
            }
            Files.write(path, lines);
        }
        static RentalShop load(Path path) throws IOException {
            RentalShop shop = new RentalShop();
            for (String line : Files.readAllLines(path)) {
                String[] part = line.split("\\|");
                if (part[0].equals("BIKE")) {
                    shop.bikes.put(part[1], new Bike(part[1], part[2], Integer.parseInt(part[3])));
                } else if (part[0].equals("RENT")) {
                    shop.rentals.add(new Rental(part[1], part[2], part[3]));
                }
            }
            return shop;
        }
    }
    static String errorOf(Runnable action) {
        try {
            action.run();
        } catch (RentalError e) {
            return "RentalError: " + e.getMessage();
        }
        return "no error";
    }
    public static void main(String[] args) throws IOException {
        // ---- 1. Build the shop ----
        System.out.println("1. Stock");
        RentalShop shop = new RentalShop();
        shop.addBike(new Bike("B1", "City Cruiser", 2));
        shop.addBike(new Bike("B2", "Hill Rider", 1));
        shop.addBike(new Bike("B1", "City Cruiser", 1));           // same id: the counts add up
        System.out.println("  free B1: " + shop.free("B1") + ", free B2: " + shop.free("B2") + ", free B9: " + shop.free("B9"));
        // ---- 2. The rules ----
        System.out.println("2. Rules raise errors");
        shop.rent("B2", "asha", "2026-11-01");
        System.out.println("  second rent of B2: " + errorOf(() -> shop.rent("B2", "ravi", "2026-11-01")));
        System.out.println("  unknown bike     : " + errorOf(() -> shop.rent("B9", "ravi", "2026-11-01")));
        shop.rent("B1", "asha", "2026-11-01");
        System.out.println("  third rental     : " + errorOf(() -> shop.rent("B1", "asha", "2026-11-01")));
        // ---- 3. Save to a file in a temporary folder, then load it back ----
        System.out.println("3. Persistence");
        Path folder = Files.createTempDirectory("rental");
        Path file = folder.resolve("shop.txt");
        shop.save(file);
        for (String line : Files.readAllLines(file)) {
            System.out.println("  file> " + line);
        }
        RentalShop again = RentalShop.load(file);
        System.out.println("  after load, free B1: " + again.free("B1") + ", free B2: " + again.free("B2"));
        // ---- 4. Fees from dates ----
        System.out.println("4. Returning and late fees");
        System.out.println("  B1 back after 1 day : Rs. " + again.giveBack("B1", "asha", "2026-11-02"));
        System.out.println("  B2 back after 4 days: Rs. " + again.giveBack("B2", "asha", "2026-11-05"));
        System.out.println("  B2 again            : " + errorOf(() -> again.giveBack("B2", "asha", "2026-11-05")));
        // ---- 5. Clean up the temporary files ----
        Files.deleteIfExists(file);
        Files.deleteIfExists(folder);
        System.out.println("5. Temporary folder removed: " + !Files.exists(folder));
    }
}
