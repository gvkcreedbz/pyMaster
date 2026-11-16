/* Day 07 - Code along: the menu-loop pattern (a tip calculator).
 *
 * Type each section yourself, run it (java Examples.java), then change values and re-run.
 * The program reads from the keyboard. To replay a saved conversation instead, run:
 *     java Examples.java < ..\..\..\_dev_tools\stdin_java\day07.txt
 */
import java.util.Locale;
import java.util.Scanner;

class Examples {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);     // ONE Scanner for the whole program
        int billsDone = 0;

        System.out.println("=== Tip calculator ===");
        while (true) {                            // keep going until the user quits
            System.out.println();
            System.out.println("1) Calculate tip   2) Show count   q) Quit");
            System.out.print("Choose: ");
            String choice = in.nextLine().trim();

            if (choice.equals("q")) {
                break;                            // leave the loop
            } else if (choice.equals("1")) {
                System.out.print("Bill amount: ");
                double bill = Double.parseDouble(in.nextLine().trim());
                if (bill <= 0) {
                    System.out.println("Bill must be positive");
                    continue;                     // back to the menu
                }
                double tip = bill * 10 / 100;
                System.out.println(String.format(Locale.US, "Tip (10%%): Rs. %.2f | Total: Rs. %.2f", tip, bill + tip));
                billsDone++;
            } else if (choice.equals("2")) {
                System.out.println("Bills calculated so far: " + billsDone);
            } else {
                System.out.println("Invalid option, try again");
            }
        }

        System.out.println("Bye!");
    }
}
