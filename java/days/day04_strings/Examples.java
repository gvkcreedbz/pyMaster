/* Day 04 - Code along: cleaning an Instagram signup form.
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 */
class Examples {
    public static void main(String[] args) {
        // ---- 1. Indexing and cutting out pieces ----
        String word = "PYTHON";
        System.out.println(word.charAt(0) + " " + word.charAt(word.length() - 1)
                + " " + word.substring(1, 4) + " " + word.substring(3) + " " + word.length());
        System.out.println(new StringBuilder(word).reverse());     // NOHTYP

        // ---- 2. Messy form input -> clean data ----
        String rawName = "   aarav   SHARMA  ";
        String rawEmail = "  Aarav.Sharma@Gmail.COM ";
        String[] parts = rawName.strip().split("\\s+");     // split on any run of spaces
        String first = parts[0].substring(0, 1).toUpperCase() + parts[0].substring(1).toLowerCase();
        String last = parts[1].substring(0, 1).toUpperCase() + parts[1].substring(1).toLowerCase();
        String email = rawEmail.strip().toLowerCase();
        System.out.println("[" + first + " " + last + "] [" + email + "]");

        // ---- 3. Splitting and joining ----
        System.out.println("First: " + first + " | Last: " + last);
        String username = (first + "." + last).toLowerCase();
        System.out.println("Suggested username: " + username);
        System.out.println(String.join("-", "2026", "11", "16"));     // 2026-11-16
        System.out.println(String.join(" ", rawName.strip().split("\\s+")));   // aarav SHARMA

        // ---- 4. Searching ----
        System.out.println("has @? " + email.contains("@") + " | domain: " + email.substring(email.indexOf("@") + 1));
        System.out.println(email.indexOf("gmail") + " " + email.indexOf("zzz") + " " + email.endsWith(".com"));

        // ---- 5. Hashtag from a caption ----
        String caption = "learning java daily!";
        String noPunct = caption.replace("!", "");
        String[] w = noPunct.split(" ");
        String hashtag = "#" + w[0].substring(0, 1).toUpperCase() + w[0].substring(1)
                + w[1].substring(0, 1).toUpperCase() + w[1].substring(1)
                + w[2].substring(0, 1).toUpperCase() + w[2].substring(1);
        System.out.println(hashtag);                    // #LearningJavaDaily

        // ---- 6. Immutability: methods return NEW strings ----
        String s = "Java";
        s.toUpperCase();                                 // result thrown away!
        System.out.println(s);                           // still Java
        s = s.toUpperCase();                             // save it
        System.out.println(s);                           // JAVA

        // ---- 7. equals vs == ----
        String typed = new String("yes");                // a brand-new text object
        System.out.println(typed == "yes");              // false: == asks "same object?"
        System.out.println(typed.equals("yes"));         // true:  equals asks "same letters?"
        System.out.println("Yes".equalsIgnoreCase("YES"));   // true
        System.out.println("apple".compareTo("banana") < 0); // true (alphabetical)

        // ---- 8. StringBuilder: build text step by step ----
        StringBuilder sb = new StringBuilder();
        sb.append("Chai").append(", ").append("Samosa");
        sb.insert(0, "Order: ");
        System.out.println(sb + " (" + sb.length() + " characters)");

        // ---- 9. String.format and text blocks ----
        String line = String.format("%-10s|%6.2f|%5d", "Chai", 20.5, 3);
        System.out.println(line);                        // Chai      | 20.50|    3
        int otp = 4821;
        String message = """
                Dear %s,
                Your OTP is %d.
                Do not share it with anyone.
                """.formatted(first, otp);
        System.out.print(message);
        System.out.println("She said \"hi\" and C:\\new");   // escapes
    }
}
