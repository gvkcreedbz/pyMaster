"""Maintainer tool: builds java/tracker/JAVA_PROGRESS_TRACKER.xlsx from the Java lessons and solutions.

    python _dev_tools/build_tracker_java.py

Reads   java/days/dayNN_*/LESSON.md          (title, scenario, quiz size, concept headings)
        java/solutions/dayNN_Solution.java   (exercise headers:  // L1-1 | Title   (Level 1 - Beginner))
Writes  java/tracker/JAVA_PROGRESS_TRACKER.xlsx   (same sheets as the Python tracker)

It never crashes when only some days exist yet: the 30-day plan always comes from the built-in syllabus
(see java/_AUTHORING.md); days whose LESSON.md / solution file exist add their real title, scenario,
quiz size, exercises and concepts. Re-run it after more days are written.

WARNING: this REBUILDS the workbook from scratch and overwrites it - any progress you typed
into the tracker is lost. Learners should never run this; they just open the .xlsx file.
Needs: python -m pip install openpyxl
"""
import datetime as dt
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "java"
OUT = JAVA / "tracker" / "JAVA_PROGRESS_TRACKER.xlsx"
START_DATE = dt.date(2026, 11, 16)
N_DAYS = 30
LEVEL_LABEL = {"1": "L1 Beginner", "2": "L2 Intermediate", "3": "L3 Challenge"}
WEEK_OF_DAY = lambda d: 1 if d <= 7 else 2 if d <= 14 else 3 if d <= 21 else 4  # noqa: E731

# Built-in syllabus (folder names and topics from java/_AUTHORING.md; scenarios from the Python twin).
SYLLABUS = [
    (1, "day01_hello_java", "Hello, Java! (How a computer follows instructions)", "A cafe receipt printer."),
    (2, "day02_variables_input", "Variables, Data Types & Scanner input", "Food-delivery bill splitter (Swiggy / Zomato / Uber Eats style)."),
    (3, "day03_numbers_operators", "Numbers, Operators, Math & BigDecimal", "E-commerce checkout + loan EMI calculator."),
    (4, "day04_strings", "Strings (Text Processing)", "Instagram signup + caption tools."),
    (5, "day05_decisions", "Decisions: if / else, switch, boolean logic", "Delivery-fee rules and ATM checks."),
    (6, "day06_loops", "Loops: for, while, do/while, break, continue", "Number-guessing game + PIN retry + processing 1,000 orders."),
    (7, "day07_week1_project_atm", "Week 1 Project: Mini ATM (and Week-1 Review)", "An ATM (and every menu-driven app)."),
    (8, "day08_arrays", "Arrays (1-D, 2-D) & the Arrays class", "A shopping cart, a Spotify playlist, a to-do app."),
    (9, "day09_lists_sets", "ArrayList, List.of, HashSet & TreeSet", "Instagram mutual friends and unique visitors."),
    (10, "day10_maps", "Maps: HashMap, TreeMap, LinkedHashMap", "Contact book, inventory, user profile, word counts."),
    (11, "day11_methods", "Methods: parameters, return, overloading, varargs, recursion", "A billing service."),
    (12, "day12_lambdas_streams", "Lambdas, Method References & Stream basics", "E-commerce filters + music charts."),
    (13, "day13_nested_data_records", "Nested Data, Records & JSON-like output", "A restaurant-listing API (Zomato/Swiggy style)."),
    (14, "day14_week2_project_expense_tracker", "Week 2 Project: Expense Tracker (and Week-2 Review)", "A personal-finance app (Splitwise / Google Pay Spends)."),
    (15, "day15_files_nio", "Files with java.nio.file", "A server log analyser."),
    (16, "day16_csv_json_files", "CSV & JSON-style Files", "A sales report from an Excel/ERP export."),
    (17, "day17_exceptions_logging", "Exceptions, try-with-resources & Logging", "A payment service."),
    (18, "day18_packages_stdlib_build_tools", "Packages, java.time, the Standard Library & Maven/Gradle basics", "A birthday/deadline reminder + a quick analytics helper."),
    (19, "day19_oop_basics", "Object-Oriented Programming I: Classes & Objects", "A banking app."),
    (20, "day20_oop_advanced", "OOP II: Inheritance, Interfaces, enum, sealed & record", "An HR/payroll system and a game."),
    (21, "day21_week3_project_library_system", "Week 3 Project: Library Management System (and Week-3 Review)", "A public-library / office-asset system."),
    (22, "day22_generics_optional_iterators", "Generics, Optional, Iterators & Functional Interfaces", "Streaming a 10-GB log file, retrying API calls, auto-closing DB connections."),
    (23, "day23_regex_clean_code", "Regular Expressions, Immutability & Clean Code", "Cleaning a messy contact/invoice dump."),
    (24, "day24_junit_git", "Testing with JUnit 5 & Git Basics", "A shop's discount code broke on Black Friday."),
    (25, "day25_collections_streams_data", "Collections Deep-Dive & Collectors on sales.csv", "You're the new analyst at an online store."),
    (26, "day26_streams_reporting", "Streams II: Cleaning, Top-N & Text Reports", "A messy weekly sales export lands on your desk."),
    (27, "day27_http_json", "HTTP & JSON with HttpClient", "A dashboard that needs live weather/posts/prices."),
    (28, "day28_jdbc_sql", "Databases: JDBC, SQLite & SQL", "Files don't scale - store and query orders with SQL."),
    (29, "day29_capstone_pipeline", "Capstone: Build a Sales Data Pipeline (ETL)", "Every Monday the store emails a messy CSV."),
    (30, "day30_rest_api_final_exam", "A REST API with HttpServer & The Final Exam", "The mobile-app team needs your data."),
]

# Extra concepts for project days (only added when that day's lesson exists).
EXTRA_CONCEPTS = {
    7: ["Menu-loop pattern (while (true) + switch)", "Input validation loops with Scanner"],
    14: ["Breaking a program into small methods", "Designing data as a List of records", "Building an interactive menu app"],
    21: ["Designing classes for a real system", "Saving and loading objects (files)", "Reports and queries over objects"],
    29: ["ETL pipeline design (Extract -> Transform -> Load -> Report)", "Logging and error handling in a pipeline", "End-to-end testing of a pipeline"],
}

# ---------- styles ----------
NAVY, BLUE, LIGHT = "1F3864", "2F5597", "DDEBF7"
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
HEAD_FILL = PatternFill("solid", fgColor=NAVY)
SUB_FILL = PatternFill("solid", fgColor=LIGHT)
GREY_FILL = PatternFill("solid", fgColor="EDEDED")
GREEN, YELLOW, RED, ORANGE, GREYC = "C6EFCE", "FFEB9C", "FFC7CE", "F8CBAD", "D9D9D9"
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WHITE_BOLD = Font(bold=True, color="FFFFFF")
TITLE_FONT = Font(size=18, bold=True, color=NAVY)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


def clean_md(text):
    text = re.sub(r"[`*⭐⚠🔒]", "", text)
    return re.sub(r"\s+", " ", text).strip()


# ---------- read the course content ----------
def read_course():
    """Returns (days, exercises, concepts, present). `days` always has 30 entries."""
    days, exercises, concepts = [], [], []
    present = []
    folders = {}
    if (JAVA / "days").is_dir():
        for f in (JAVA / "days").glob("day*"):
            m = re.match(r"day(\d\d)", f.name)
            if m and f.is_dir():
                folders[int(m.group(1))] = f

    for n, folder_name, title, scenario in SYLLABUS:
        quiz_total = 0
        folder = folders.get(n)
        lesson = folder / "LESSON.md" if folder else None
        if lesson is not None and lesson.is_file():
            present.append(n)
            folder_name = folder.name
            text = lesson.read_text(encoding="utf-8")
            first = text.splitlines()[0] if text.strip() else ""
            m = re.match(r"#\s+Day\s+\d+\s*[—–-]\s*(.+)", first)
            if m:
                title = clean_md(m.group(1))

            m = re.search(r"^##\s+🌍[^\n]*\n+(.+?)(?:\n\n|\Z)", text, re.M | re.S)
            if m:
                scenario = clean_md(m.group(1).split("Trend:")[0])
                if len(scenario) > 150:
                    scenario = scenario[:147].rsplit(" ", 1)[0] + "…"

            q = re.search(r"^##\s+\d+\.\s+Quiz.*?\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
            if q:
                quiz_total = len(re.findall(r"^\d+\.\s", q.group(1), re.M))

            for h in re.findall(r"^###\s+(?:\d+\.\d+\s+)?(.+)$", text, re.M):
                h = clean_md(h)
                if not h.lower().startswith("where to go"):
                    concepts.append((n, h))

            for item in EXTRA_CONCEPTS.get(n, []):
                concepts.append((n, item))

        days.append({"n": n, "title": title, "scenario": scenario, "quiz": quiz_total or 8, "folder": folder_name})

        # exercises come from the solution file (any capitalisation of the file name)
        sol_path = next(iter(sorted((JAVA / "solutions").glob(f"day{n:02d}_[Ss]olution.java"))), None) if (JAVA / "solutions").is_dir() else None
        if sol_path is not None:
            sol = sol_path.read_text(encoding="utf-8")
            seen = set()
            for ex_id, name, level in re.findall(r"^\s*//\s+(L\d-\d)\s+\|\s+(.+?)\s+\(Level\s+(\d)", sol, re.M):
                if ex_id not in seen and level in LEVEL_LABEL:
                    seen.add(ex_id)
                    exercises.append((n, ex_id, name.strip(), LEVEL_LABEL[level]))

    concepts.sort(key=lambda c: c[0])  # stable: keeps lesson order inside a day
    return days, exercises, concepts, present


# ---------- helpers ----------
def title_block(ws, title, subtitle=None):
    ws["A1"] = title
    ws["A1"].font = TITLE_FONT
    if subtitle:
        ws["A2"] = subtitle
        ws["A2"].font = Font(italic=True, color="595959")
    ws.sheet_view.showGridLines = False


def header_row(ws, row, headers, widths=None):
    for col, text in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=text)
        cell.fill, cell.font, cell.alignment, cell.border = HEAD_FILL, WHITE_BOLD, CENTER, BORDER
    ws.row_dimensions[row].height = 32
    if widths:
        for col, width in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width


def style_range(ws, first_row, last_row, last_col, input_cols=(), wrap_cols=(), center_cols=(), formats=None):
    for r in range(first_row, last_row + 1):
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BORDER
            if c in input_cols:
                cell.fill = INPUT_FILL
            if c in wrap_cols:
                cell.alignment = WRAP
            if c in center_cols:
                cell.alignment = Alignment(horizontal="center", vertical="top")
            if formats and c in formats:
                cell.number_format = formats[c]


def add_list_validation(ws, cell_range, source, prompt=None):
    dv = DataValidation(type="list", formula1=source, allow_blank=True, showDropDown=False)
    if prompt:
        dv.promptTitle, dv.prompt, dv.showInputMessage = "Choose", prompt, True
    ws.add_data_validation(dv)
    dv.add(cell_range)


def fill_rule(ws, cell_range, formula, color, bold=False):
    ws.conditional_formatting.add(cell_range, FormulaRule(formula=[formula], fill=PatternFill("solid", bgColor=color, fgColor=color),
                                                          font=Font(bold=True) if bold else None))


def style_chart(chart, title, x_title=None, y_title=None, width=15.5, height=7.5):
    chart.title, chart.width, chart.height = title, width, height
    if x_title:
        chart.x_axis.title = x_title
    if y_title:
        chart.y_axis.title = y_title
    if chart.legend is not None:
        chart.legend.position = "b"          # bottom, so it never covers the bars
        chart.legend.overlay = False
    chart.varyColors = False                 # one colour per series (not per point)
    chart.x_axis.delete = False
    chart.y_axis.delete = False


# ---------- build ----------
def build():
    days, exercises, concepts, present = read_course()
    n_days, n_ex, n_con = len(days), len(exercises), len(concepts)
    assert n_days == N_DAYS, f"expected {N_DAYS} days, found {n_days}"

    wb = Workbook()
    ws_start = wb.active
    ws_start.title = "START HERE"
    ws_dash = wb.create_sheet("Dashboard")
    ws_plan = wb.create_sheet("Daily Plan")
    ws_ex = wb.create_sheet("Exercise Log")
    ws_con = wb.create_sheet("Concept Checklist")
    ws_proj = wb.create_sheet("Projects")
    ws_week = wb.create_sheet("Weekly Review")
    ws_time = wb.create_sheet("Time Log")
    ws_bug = wb.create_sheet("Bug Journal")
    ws_set = wb.create_sheet("Settings")

    PLAN_FIRST, PLAN_LAST = 5, 4 + n_days
    EX_FIRST, EX_LAST = 5, max(5, 4 + n_ex)       # never an empty/inverted range, even with 0 exercises
    CON_FIRST, CON_LAST = 5, max(5, 4 + n_con)
    BUG_FIRST, BUG_LAST = 5, 204
    TIME_FIRST, TIME_LAST = 5, 154

    # ===== Settings =====
    title_block(ws_set, "Settings & dropdown lists", "Yellow cells are yours to change. Everything else updates automatically.")
    ws_set["A4"], ws_set["B4"] = "Start date (Day 1)", START_DATE
    ws_set["A5"], ws_set["B5"] = "Planned hours per day", 2
    ws_set["A6"], ws_set["B6"] = "Programme length (days)", n_days
    for r in (4, 5):
        ws_set.cell(row=r, column=2).fill = INPUT_FILL
        ws_set.cell(row=r, column=2).border = BORDER
    ws_set["B4"].number_format = "ddd dd-mmm-yyyy"
    ws_set["A8"] = "Changing the start date shifts every date in 'Daily Plan'. Missed days? Don't edit the dates - follow the catch-up rule in java/00_GAME_PLAN.md."
    ws_set["A8"].alignment = WRAP
    ws_set.merge_cells("A8:B10")
    lists = {
        "D": ("Day status", ["Not started", "In progress", "Done", "Skipped"]),
        "E": ("Exercise status", ["Not started", "Attempted", "Passed alone", "Passed with hints", "Viewed solution"]),
        "F": ("Activity", ["Lesson", "Code-along", "Practice", "Quiz", "Review", "Project", "Debugging", "Other"]),
        "G": ("Bug type", ["Compile: cannot find symbol", "Compile: ; expected / syntax", "Compile: incompatible types", "Compile: missing return / unreachable",
                           "NullPointerException", "ArrayIndexOutOfBounds / IndexOutOfBounds", "NumberFormatException", "InputMismatchException",
                           "ClassCastException", "IOException / NoSuchFileException", "ConcurrentModificationException", "Logic bug", "Other"]),
        "H": ("Project status", ["Not started", "In progress", "Works!", "Polished + stretch goals"]),
        "I": ("Yes / No", ["Yes", "Partly", "No"]),
    }
    for col, (name, items) in lists.items():
        ws_set[f"{col}3"] = name
        ws_set[f"{col}3"].font = WHITE_BOLD
        ws_set[f"{col}3"].fill = HEAD_FILL
        for i, item in enumerate(items):
            ws_set[f"{col}{4 + i}"] = item
        ws_set.column_dimensions[col].width = 26 if col == "G" else 22
    ws_set.column_dimensions["A"].width = 30
    ws_set.column_dimensions["B"].width = 20
    ws_set.column_dimensions["C"].width = 4

    def src(col):
        return f"=Settings!${col}$4:${col}${3 + len(lists[col][1])}"

    # ===== Daily Plan =====
    title_block(ws_plan, "Daily Plan - 30 days, 2 hours a day", "Pick the status in column I, type your hours and quiz score. Yellow = you type, white = automatic.")
    headers = ["Day", "Date", "Weekday", "Week", "Topic", "Real-world scenario", "Lesson file (click)", "Planned hrs", "Status",
               "Actual hrs", "Quiz correct", "Quiz total", "Quiz %", "Exercises passed", "Exercises total", "Confidence (1-5)", "Notes",
               "Streak (helper)", "Quiz % (chart helper)"]
    header_row(ws_plan, 4, headers, [6, 14, 9, 7, 38, 60, 22, 9, 14, 9, 9, 8, 9, 11, 11, 11, 36, 9, 11])
    for i, d in enumerate(days):
        r = PLAN_FIRST + i
        ws_plan.cell(row=r, column=1, value=d["n"])
        ws_plan.cell(row=r, column=2, value=f"=Settings!$B$4+A{r}-1")
        ws_plan.cell(row=r, column=3, value=f'=TEXT(B{r},"ddd")')
        ws_plan.cell(row=r, column=4, value=WEEK_OF_DAY(d["n"]))
        ws_plan.cell(row=r, column=5, value=d["title"])
        ws_plan.cell(row=r, column=6, value=d["scenario"])
        link = ws_plan.cell(row=r, column=7, value=f"{d['folder']}/LESSON.md")
        link.hyperlink = f"../days/{d['folder']}/LESSON.md"
        link.font = Font(color="0563C1", underline="single")
        ws_plan.cell(row=r, column=8, value="=Settings!$B$5")
        ws_plan.cell(row=r, column=9, value="Not started")
        ws_plan.cell(row=r, column=12, value=d["quiz"])
        ws_plan.cell(row=r, column=13, value=f'=IF(AND(ISNUMBER(K{r}),L{r}>0),K{r}/L{r},"")')
        ws_plan.cell(row=r, column=14, value=f"=COUNTIFS('Exercise Log'!$A${EX_FIRST}:$A${EX_LAST},A{r},'Exercise Log'!$E${EX_FIRST}:$E${EX_LAST},\"Passed*\")")
        ws_plan.cell(row=r, column=15, value=f"=COUNTIF('Exercise Log'!$A${EX_FIRST}:$A${EX_LAST},A{r})")
        ws_plan.cell(row=r, column=18, value=f'=IF(I{r}="Done",1,0)' if i == 0 else f'=IF(I{r}="Done",R{r - 1}+1,0)')
        ws_plan.cell(row=r, column=19, value=f"=IF(ISNUMBER(M{r}),M{r},NA())")
    style_range(ws_plan, PLAN_FIRST, PLAN_LAST, 19, input_cols=(9, 10, 11, 16, 17), wrap_cols=(5, 6, 17), center_cols=(1, 3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19),
                formats={2: "dd-mmm-yyyy", 13: "0%", 19: "0%", 8: "0.0", 10: "0.0"})
    for r in range(PLAN_FIRST, PLAN_LAST + 1):
        ws_plan.row_dimensions[r].height = 32
        for c in (18, 19):
            ws_plan.cell(row=r, column=c).font = Font(color="808080", size=9)
    add_list_validation(ws_plan, f"I{PLAN_FIRST}:I{PLAN_LAST}", src("D"))
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
    ws_plan.add_data_validation(dv)
    dv.add(f"P{PLAN_FIRST}:P{PLAN_LAST}")
    dv = DataValidation(type="decimal", operator="between", formula1="0", formula2="12", allow_blank=True)
    ws_plan.add_data_validation(dv)
    dv.add(f"J{PLAN_FIRST}:J{PLAN_LAST}")
    area = f"A{PLAN_FIRST}:Q{PLAN_LAST}"
    fill_rule(ws_plan, area, f'$I{PLAN_FIRST}="Done"', GREEN)
    fill_rule(ws_plan, area, f'$I{PLAN_FIRST}="Skipped"', GREYC)
    fill_rule(ws_plan, area, f'$I{PLAN_FIRST}="In progress"', YELLOW)
    fill_rule(ws_plan, area, f"$B{PLAN_FIRST}=TODAY()", "BDD7EE", bold=True)
    fill_rule(ws_plan, f"B{PLAN_FIRST}:B{PLAN_LAST}", f'AND($B{PLAN_FIRST}<TODAY(),$I{PLAN_FIRST}<>"Done",$I{PLAN_FIRST}<>"Skipped")', RED)
    ws_plan.freeze_panes = "F5"
    ws_plan.auto_filter.ref = f"A4:S{PLAN_LAST}"
    ws_plan["F2"] = "Red date = that day is in the past and not marked Done/Skipped (you're behind)."
    ws_plan["F2"].font = Font(italic=True, color="C00000")

    # ===== Exercise Log =====
    title_block(ws_ex, f"Exercise Log - {n_ex} graded exercises", "After running java Practice.java: choose a status. 'Passed alone' = no hints, 'Passed with hints' = used the hint ladder.")
    header_row(ws_ex, 4, ["Day", "ID", "Exercise", "Level", "Status", "Attempts", "Minutes", "Hint level used (0-3)", "Date done", "Notes"],
               [6, 8, 36, 17, 18, 10, 10, 12, 14, 44])
    for i, (n, ex_id, name, level) in enumerate(exercises):
        r = EX_FIRST + i
        for c, v in enumerate([n, ex_id, name, level, "Not started"], 1):
            ws_ex.cell(row=r, column=c, value=v)
    if n_ex:
        style_range(ws_ex, EX_FIRST, EX_LAST, 10, input_cols=(5, 6, 7, 8, 9, 10), center_cols=(1, 2, 4, 5, 6, 7, 8, 9), formats={9: "dd-mmm-yyyy"})
    add_list_validation(ws_ex, f"E{EX_FIRST}:E{EX_LAST}", src("E"))
    dv = DataValidation(type="whole", operator="between", formula1="0", formula2="3", allow_blank=True)
    ws_ex.add_data_validation(dv)
    dv.add(f"H{EX_FIRST}:H{EX_LAST}")
    area = f"A{EX_FIRST}:E{EX_LAST}"
    fill_rule(ws_ex, area, f'$E{EX_FIRST}="Passed alone"', GREEN)
    fill_rule(ws_ex, area, f'$E{EX_FIRST}="Passed with hints"', "E2EFDA")
    fill_rule(ws_ex, area, f'$E{EX_FIRST}="Attempted"', YELLOW)
    fill_rule(ws_ex, area, f'$E{EX_FIRST}="Viewed solution"', ORANGE)
    ws_ex.freeze_panes = "D5"
    ws_ex.auto_filter.ref = f"A4:J{EX_LAST}"

    # ===== Concept Checklist =====
    title_block(ws_con, f"Concept Checklist - {n_con} ideas you will meet", "Rate your confidence 1-5 (5 = I could teach it). Revisit anything below 4 in your weekly review.")
    header_row(ws_con, 4, ["#", "Concept", "Taught on day", "Week", "Confidence (1-5)", "Can explain without notes?", "Last reviewed", "Notes"],
               [6, 62, 12, 8, 14, 18, 14, 40])
    for i, (n, concept) in enumerate(concepts):
        r = CON_FIRST + i
        for c, v in enumerate([i + 1, concept, n, WEEK_OF_DAY(n)], 1):
            ws_con.cell(row=r, column=c, value=v)
    if n_con:
        style_range(ws_con, CON_FIRST, CON_LAST, 8, input_cols=(5, 6, 7, 8), wrap_cols=(2,), center_cols=(1, 3, 4, 5, 6, 7), formats={7: "dd-mmm-yyyy"})
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
    ws_con.add_data_validation(dv)
    dv.add(f"E{CON_FIRST}:E{CON_LAST}")
    add_list_validation(ws_con, f"F{CON_FIRST}:F{CON_LAST}", src("I"))
    fill_rule(ws_con, f"E{CON_FIRST}:E{CON_LAST}", f"AND(ISNUMBER($E{CON_FIRST}),$E{CON_FIRST}>=4)", GREEN)
    fill_rule(ws_con, f"E{CON_FIRST}:E{CON_LAST}", f"AND(ISNUMBER($E{CON_FIRST}),$E{CON_FIRST}=3)", YELLOW)
    fill_rule(ws_con, f"E{CON_FIRST}:E{CON_LAST}", f"AND(ISNUMBER($E{CON_FIRST}),$E{CON_FIRST}<=2)", RED)
    ws_con.freeze_panes = "C5"
    ws_con.auto_filter.ref = f"A4:H{CON_LAST}"

    # ===== Projects =====
    title_block(ws_proj, "Projects & Portfolio", "Five milestone projects are built into the plan. Add your GitHub links as you go.")
    header_row(ws_proj, 4, ["Project", "Day", "What you build", "Status", "Stretch goals done?", "Link / folder", "What I learned"], [34, 7, 54, 22, 18, 36, 50])
    projects = [
        ("Week 1: Mini ATM", 7, "Menu loop with Scanner, validation, balance logic - a complete interactive program"),
        ("Week 2: Expense Tracker", 14, "Records + lists + maps + streams, budget report, interactive menu"),
        ("Week 3: Library Management System", 21, "OOP design, checkout/return rules, save/load to files, reports"),
        ("Capstone: Sales Data Pipeline", 29, "Messy CSV -> clean data -> SQLite (JDBC) -> KPIs -> text report, as a command-line tool"),
        ("Finale: Mini Shop REST API", 30, "JDK HttpServer: routes, JSON, status codes, sales endpoints from your CSV"),
    ]
    for i, (name, day, what) in enumerate(projects):
        r = 5 + i
        for c, v in enumerate([name, day, what, "Not started"], 1):
            ws_proj.cell(row=r, column=c, value=v)
    style_range(ws_proj, 5, 9, 7, input_cols=(4, 5, 6, 7), wrap_cols=(1, 3, 7), center_cols=(2, 4, 5))
    for r in range(5, 10):
        ws_proj.row_dimensions[r].height = 36
    add_list_validation(ws_proj, "D5:D9", src("H"))
    add_list_validation(ws_proj, "E5:E9", src("I"))
    fill_rule(ws_proj, "A5:D9", '$D5="Works!"', GREEN)
    fill_rule(ws_proj, "A5:D9", '$D5="Polished + stretch goals"', "A9D08E")
    fill_rule(ws_proj, "A5:D9", '$D5="In progress"', YELLOW)
    ws_proj["A12"] = "Portfolio ideas for AFTER Day 30 (pick one per month)"
    ws_proj["A12"].font = Font(bold=True, size=13, color=NAVY)
    ideas = [
        "Expense API: Spring Boot + JPA + PostgreSQL service with validation and tests (JUnit + Mockito)",
        "Price tracker: poll a product API with HttpClient, store history in a database, alert when it drops",
        "Personal finance CLI: import bank CSVs, categorise spending with streams, monthly text/HTML reports",
        "Log analyser: parse server logs with regex and streams, find error spikes, print a chart",
        "Library / inventory app: the Week-3 system rebuilt on Spring Boot with a real database",
        "Study-notes search: index your notes and answer questions with an LLM API (HttpClient + JSON)",
        "File organiser: sort Downloads by type/date with java.nio.file, logging and a dry-run mode",
        "Quiz app: questions in JSON, scoring, leaderboard in SQLite/H2, packaged as a runnable JAR",
        "Concurrency playground: producer/consumer with ExecutorService and CompletableFuture, with tests",
        "Dockerised service: containerise your REST API with a multi-stage Dockerfile and deploy it",
    ]
    for i, idea in enumerate(ideas):
        ws_proj[f"A{13 + i}"] = f"{i + 1}. {idea}"
        ws_proj.merge_cells(f"A{13 + i}:G{13 + i}")

    # ===== Weekly Review =====
    title_block(ws_week, "Weekly Review - 15 minutes at the end of every week", "Numbers fill in automatically. Be honest in the yellow cells - this is where learning sticks.")
    header_row(ws_week, 4, ["Week", "Days done", "Days planned", "Planned hrs", "Actual hrs", "Avg quiz %", "Exercises passed %", "Biggest win",
                            "Hardest topic", "Bug that taught me most", "Do differently next week", "Energy (1-5)", "Ready for next week?"],
               [8, 10, 11, 11, 10, 11, 14, 36, 30, 34, 34, 11, 16])
    for w in range(1, 5):
        r = 4 + w
        plan = f"'Daily Plan'!$D${PLAN_FIRST}:$D${PLAN_LAST}"
        ws_week.cell(row=r, column=1, value=w)
        ws_week.cell(row=r, column=2, value=f"=COUNTIFS({plan},A{r},'Daily Plan'!$I${PLAN_FIRST}:$I${PLAN_LAST},\"Done\")")
        ws_week.cell(row=r, column=3, value=f"=COUNTIF({plan},A{r})")
        ws_week.cell(row=r, column=4, value=f"=SUMIFS('Daily Plan'!$H${PLAN_FIRST}:$H${PLAN_LAST},{plan},A{r})")
        ws_week.cell(row=r, column=5, value=f"=SUMIFS('Daily Plan'!$J${PLAN_FIRST}:$J${PLAN_LAST},{plan},A{r})")
        ws_week.cell(row=r, column=6, value=f"=IFERROR(AVERAGEIFS('Daily Plan'!$M${PLAN_FIRST}:$M${PLAN_LAST},{plan},A{r}),\"\")")
        ex_total = f"SUMIFS('Daily Plan'!$O${PLAN_FIRST}:$O${PLAN_LAST},{plan},A{r})"
        ex_done = f"SUMIFS('Daily Plan'!$N${PLAN_FIRST}:$N${PLAN_LAST},{plan},A{r})"
        ws_week.cell(row=r, column=7, value=f"=IF({ex_total}=0,\"\",{ex_done}/{ex_total})")
        ws_week.row_dimensions[r].height = 60
    style_range(ws_week, 5, 8, 13, input_cols=(8, 9, 10, 11, 12, 13), wrap_cols=(8, 9, 10, 11), center_cols=(1, 2, 3, 4, 5, 6, 7, 12, 13),
                formats={6: "0%", 7: "0%", 4: "0.0", 5: "0.0"})
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
    ws_week.add_data_validation(dv)
    dv.add("L5:L8")
    add_list_validation(ws_week, "M5:M8", src("I"))
    ws_week["A11"] = "Review questions to answer in your notes"
    ws_week["A11"].font = Font(bold=True, size=13, color=NAVY)
    prompts = [
        "1. Explain this week's hardest concept in 3 sentences, as if to a friend. Where did you get stuck explaining?",
        "2. Open an old exercise you solved on day 1 of the week. Can you solve it again in half the time?",
        "3. What did your Bug Journal teach you? Which compiler message did you learn to read?",
        "4. Which concepts in the checklist are still below 4? Plan 20 minutes for each in the next catch-up slot.",
        "5. Behind schedule? Apply the 60-minute minimum-viable-day rule: lesson + code-along + only the Level 1-2 exercises.",
    ]
    for i, p in enumerate(prompts):
        ws_week[f"A{12 + i}"] = p
        ws_week.merge_cells(f"A{12 + i}:K{12 + i}")

    # ===== Time Log =====
    title_block(ws_time, "Time Log (optional but powerful)", "Log study blocks: date, start, end. Minutes are calculated. Use 24h times like 19:30.")
    header_row(ws_time, 4, ["Date", "Start", "End", "Minutes", "Day #", "Activity", "Focus (1-5)", "Notes"], [14, 9, 9, 10, 8, 16, 11, 46])
    for r in range(TIME_FIRST, TIME_LAST + 1):
        ws_time.cell(row=r, column=4, value=f'=IF(AND(ISNUMBER(B{r}),ISNUMBER(C{r})),ROUND((C{r}-B{r})*1440,0),"")')
    style_range(ws_time, TIME_FIRST, TIME_LAST, 8, input_cols=(1, 2, 3, 5, 6, 7, 8), center_cols=(1, 2, 3, 4, 5, 6, 7), formats={1: "dd-mmm-yyyy", 2: "hh:mm", 3: "hh:mm"})
    add_list_validation(ws_time, f"F{TIME_FIRST}:F{TIME_LAST}", src("F"))
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
    ws_time.add_data_validation(dv)
    dv.add(f"G{TIME_FIRST}:G{TIME_LAST}")
    ws_time["J4"], ws_time["K4"], ws_time["L4"] = "Activity", "Minutes", "Hours"
    for c in ("J4", "K4", "L4"):
        ws_time[c].fill, ws_time[c].font, ws_time[c].alignment = HEAD_FILL, WHITE_BOLD, CENTER
    for i, act in enumerate(lists["F"][1]):
        r = 5 + i
        ws_time[f"J{r}"] = act
        ws_time[f"K{r}"] = f"=SUMIF($F${TIME_FIRST}:$F${TIME_LAST},J{r},$D${TIME_FIRST}:$D${TIME_LAST})"
        ws_time[f"L{r}"] = f"=K{r}/60"
        ws_time[f"L{r}"].number_format = "0.0"
    total_row = 5 + len(lists["F"][1])
    ws_time[f"J{total_row}"], ws_time[f"K{total_row}"], ws_time[f"L{total_row}"] = "TOTAL", f"=SUM(K5:K{total_row - 1})", f"=K{total_row}/60"
    ws_time[f"L{total_row}"].number_format = "0.0"
    for c in (f"J{total_row}", f"K{total_row}", f"L{total_row}"):
        ws_time[c].font = Font(bold=True)
    for col, width in (("J", 14), ("K", 10), ("L", 10)):
        ws_time.column_dimensions[col].width = width
    ws_time.freeze_panes = "A5"

    # ===== Bug Journal =====
    title_block(ws_bug, "Bug Journal - your secret weapon", "Every error is a lesson. Write it down once and you will recognise it forever. Pros keep notes like this.")
    header_row(ws_bug, 4, ["#", "Date", "Day", "Error type", "Error message / what went wrong", "Root cause", "How I fixed it", "Lesson (one sentence)"], [6, 14, 7, 30, 44, 36, 36, 40])
    for r in range(BUG_FIRST, BUG_LAST + 1):
        ws_bug.cell(row=r, column=1, value=f'=IF(B{r}="","",ROW()-{BUG_FIRST - 1})')
    style_range(ws_bug, BUG_FIRST, BUG_LAST, 8, input_cols=(2, 3, 4, 5, 6, 7, 8), wrap_cols=(5, 6, 7, 8), center_cols=(1, 2, 3, 4), formats={2: "dd-mmm-yyyy"})
    add_list_validation(ws_bug, f"D{BUG_FIRST}:D{BUG_LAST}", src("G"))
    ws_bug["J4"], ws_bug["K4"] = "Error type", "Times"
    for c in ("J4", "K4"):
        ws_bug[c].fill, ws_bug[c].font, ws_bug[c].alignment = HEAD_FILL, WHITE_BOLD, CENTER
    bug_types = lists["G"][1]
    for i, bug in enumerate(bug_types):
        r = 5 + i
        ws_bug[f"J{r}"] = bug
        ws_bug[f"K{r}"] = f"=COUNTIF($D${BUG_FIRST}:$D${BUG_LAST},J{r})"
    ws_bug.column_dimensions["J"].width = 38
    ws_bug.column_dimensions["K"].width = 8
    chart = BarChart()
    chart.type = "bar"
    chart.add_data(Reference(ws_bug, min_col=11, min_row=4, max_row=4 + len(bug_types)), titles_from_data=True)
    chart.set_categories(Reference(ws_bug, min_col=10, min_row=5, max_row=4 + len(bug_types)))
    chart.legend = None
    style_chart(chart, "Which bugs bite me most?", width=15, height=9)
    ws_bug.add_chart(chart, "J21")
    ws_bug.freeze_panes = "A5"

    # ===== Dashboard =====
    title_block(ws_dash, "Java in 30 Days - Dashboard")
    ws_dash["A2"] = '="Start: "&TEXT(Settings!B4,"ddd dd mmm yyyy")&"    |    Today: "&TEXT(TODAY(),"ddd dd mmm yyyy")&"    |    Finish line: "&TEXT(Settings!B4+Settings!B6-1,"ddd dd mmm yyyy")'
    ws_dash["A2"].font = Font(italic=True, color="595959")
    ws_dash.column_dimensions["A"].width = 2
    ws_dash.column_dimensions["B"].width = 34
    ws_dash.column_dimensions["C"].width = 24
    ws_dash.column_dimensions["D"].width = 26
    ws_dash.column_dimensions["E"].width = 3
    for col in "FGHIJK":
        ws_dash.column_dimensions[col].width = 15
    P = lambda col: f"'Daily Plan'!${col}${PLAN_FIRST}:${col}${PLAN_LAST}"  # noqa: E731
    X = lambda col: f"'Exercise Log'!${col}${EX_FIRST}:${col}${EX_LAST}"  # noqa: E731
    kpis = [
        ("Today is day #", "=MIN(30,MAX(0,TODAY()-Settings!B4+1))", "0"),
        ("Days completed", f'=COUNTIF({P("I")},"Done")', "0"),
        ("Overall progress", "=C6/Settings!B6", "0%"),
        ("Schedule status", '=IF(C5=0,"Not started yet",IF(C6>=C5,"AHEAD of schedule",IF(C6>=C5-1,"ON TRACK","BEHIND by "&(C5-1-C6)&" day(s) - catch up!")))', "@"),
        ("Planned hours so far", f'=SUMIFS({P("H")},{P("B")},"<="&TODAY())', "0.0"),
        ("Actual hours logged", f'=SUM({P("J")})', "0.0"),
        ("Hours vs plan so far", '=IF(C9=0,0,C10/C9)', "0%"),
        ("Longest streak (days)", f'=MAX({P("R")})', "0"),
        ("Exercises passed", f'=COUNTIF({X("E")},"Passed*")', "0"),
        ("Exercise completion", f"=IF(COUNTA({X('B')})=0,0,C13/COUNTA({X('B')}))", "0%"),
        ("Passed without hints", f'=IF(C13=0,0,COUNTIF({X("E")},"Passed alone")/C13)', "0%"),
        ("Average quiz score", f'=IFERROR(AVERAGE({P("M")}),0)', "0%"),
        ("Concepts at confidence 4-5", f"=IF(COUNTA('Concept Checklist'!$B${CON_FIRST}:$B${CON_LAST})=0,0,COUNTIF('Concept Checklist'!$E${CON_FIRST}:$E${CON_LAST},\">=4\")/COUNTA('Concept Checklist'!$B${CON_FIRST}:$B${CON_LAST}))", "0%"),
        ("Bugs logged (keep going!)", f"=COUNT('Bug Journal'!$B${BUG_FIRST}:$B${BUG_LAST})", "0"),
        ("Final exam score (of 27)", None, "0"),
    ]
    ws_dash["B4"], ws_dash["C4"] = "Metric", "Value"
    for c in ("B4", "C4"):
        ws_dash[c].fill, ws_dash[c].font, ws_dash[c].alignment, ws_dash[c].border = HEAD_FILL, WHITE_BOLD, CENTER, BORDER
    for i, (label, formula, fmt) in enumerate(kpis):
        r = 5 + i
        ws_dash[f"B{r}"] = label
        ws_dash[f"B{r}"].fill, ws_dash[f"B{r}"].border, ws_dash[f"B{r}"].font = SUB_FILL, BORDER, Font(bold=True)
        cell = ws_dash[f"C{r}"]
        if formula is not None:
            cell.value = formula
        else:
            cell.fill = INPUT_FILL
        cell.number_format, cell.border, cell.alignment = fmt, BORDER, Alignment(horizontal="center")
        cell.font = Font(bold=True, size=12)
    exam_row = 5 + len(kpis) - 1
    ws_dash[f"D{exam_row}"] = f'=IF(C{exam_row}="","<- type your score after Day 30",IF(C{exam_row}>=24,"Pro reader!",IF(C{exam_row}>=19,"Solid upper-intermediate",IF(C{exam_row}>=13,"Good foundation - review weak days","Revisit Weeks 1-2, then retake"))))'
    ws_dash[f"D{exam_row}"].font = Font(italic=True)
    fill_rule(ws_dash, "C8", 'ISNUMBER(SEARCH("BEHIND",$C$8))', RED, bold=True)
    fill_rule(ws_dash, "C8", 'OR(ISNUMBER(SEARCH("ON TRACK",$C$8)),ISNUMBER(SEARCH("AHEAD",$C$8)))', GREEN, bold=True)
    fill_rule(ws_dash, "C7", "$C$7>=1", "A9D08E")

    # weekly table
    ws_dash["F4"] = "Weekly summary"
    ws_dash["F4"].font = Font(bold=True, size=12, color=NAVY)
    for col, text in enumerate(["Week", "Days planned", "Days done", "Planned hrs", "Actual hrs", "Avg quiz %"], 6):
        cell = ws_dash.cell(row=5, column=col, value=text)
        cell.fill, cell.font, cell.alignment, cell.border = HEAD_FILL, WHITE_BOLD, CENTER, BORDER
    for w in range(1, 5):
        r = 5 + w
        ws_dash.cell(row=r, column=6, value=f"Week {w}")
        ws_dash.cell(row=r, column=7, value=f"='Weekly Review'!C{4 + w}")
        ws_dash.cell(row=r, column=8, value=f"='Weekly Review'!B{4 + w}")
        ws_dash.cell(row=r, column=9, value=f"='Weekly Review'!D{4 + w}")
        ws_dash.cell(row=r, column=10, value=f"='Weekly Review'!E{4 + w}")
        ws_dash.cell(row=r, column=11, value=f"='Weekly Review'!F{4 + w}")
        for c in range(6, 12):
            ws_dash.cell(row=r, column=c).border = BORDER
            ws_dash.cell(row=r, column=c).alignment = Alignment(horizontal="center")
        ws_dash.cell(row=r, column=11).number_format = "0%"
        ws_dash.cell(row=r, column=9).number_format = "0.0"
        ws_dash.cell(row=r, column=10).number_format = "0.0"

    # exercise level table
    ws_dash["F12"] = "Exercises by level"
    ws_dash["F12"].font = Font(bold=True, size=12, color=NAVY)
    for col, text in enumerate(["Level", "Total", "Passed", "% passed"], 6):
        cell = ws_dash.cell(row=13, column=col, value=text)
        cell.fill, cell.font, cell.alignment, cell.border = HEAD_FILL, WHITE_BOLD, CENTER, BORDER
    for i, label in enumerate(LEVEL_LABEL.values()):
        r = 14 + i
        ws_dash.cell(row=r, column=6, value=label)
        ws_dash.cell(row=r, column=7, value=f'=COUNTIF({X("D")},F{r})')
        ws_dash.cell(row=r, column=8, value=f'=COUNTIFS({X("D")},F{r},{X("E")},"Passed*")')
        ws_dash.cell(row=r, column=9, value=f"=IF(G{r}=0,0,H{r}/G{r})")
        ws_dash.cell(row=r, column=9).number_format = "0%"
        for c in range(6, 10):
            ws_dash.cell(row=r, column=c).border = BORDER
            ws_dash.cell(row=r, column=c).alignment = Alignment(horizontal="center")

    # charts
    c1 = BarChart()
    c1.type = "col"
    c1.add_data(Reference(ws_dash, min_col=9, max_col=10, min_row=5, max_row=9), titles_from_data=True)
    c1.set_categories(Reference(ws_dash, min_col=6, min_row=6, max_row=9))
    style_chart(c1, "Hours per week: planned vs actual")
    ws_dash.add_chart(c1, "B22")

    c2 = BarChart()
    c2.type = "col"
    c2.add_data(Reference(ws_dash, min_col=7, max_col=8, min_row=13, max_row=16), titles_from_data=True)
    c2.set_categories(Reference(ws_dash, min_col=6, min_row=14, max_row=16))
    style_chart(c2, "Exercises: total vs passed, by level")
    ws_dash.add_chart(c2, "F22")

    c3 = LineChart()
    c3.add_data(Reference(ws_plan, min_col=19, min_row=4, max_row=PLAN_LAST), titles_from_data=True)
    c3.set_categories(Reference(ws_plan, min_col=1, min_row=PLAN_FIRST, max_row=PLAN_LAST))
    c3.series[0].marker.symbol = "circle"
    c3.legend = None
    c3.y_axis.scaling.min, c3.y_axis.scaling.max = 0, 1
    c3.y_axis.number_format = "0%"
    style_chart(c3, "Quiz score by day number (%)")
    ws_dash.add_chart(c3, "B38")

    c4 = BarChart()
    c4.type = "col"
    c4.add_data(Reference(ws_dash, min_col=7, max_col=8, min_row=5, max_row=9), titles_from_data=True)
    c4.set_categories(Reference(ws_dash, min_col=6, min_row=6, max_row=9))
    style_chart(c4, "Days planned vs days done, by week")
    ws_dash.add_chart(c4, "F38")

    # ===== START HERE =====
    title_block(ws_start, "Java in 30 Days - Progress Tracker")
    ws_start.column_dimensions["A"].width = 3
    ws_start.column_dimensions["B"].width = 26
    ws_start.column_dimensions["C"].width = 100
    rows = [
        ("How to use this workbook", None),
        ("Colour code", "Yellow cells = you type or choose.  White/grey cells = formulas (don't type there).  Green = done, red = behind."),
        ("Every study day (5 min)", "1) Daily Plan: set the day's Status, hours, quiz score.  2) Exercise Log: set each exercise's status.  3) Bug Journal: log any new error.  4) Rate new concepts in Concept Checklist."),
        ("Every Sunday (15 min)", "Weekly Review: answer the questions, check the Dashboard. Behind? Use the catch-up rule in java/00_GAME_PLAN.md."),
        ("Dashboard", "Progress %, on-track status, hours vs plan, streak, exercise stats, quiz average, 4 charts. Type your final exam score in the yellow cell."),
        ("Daily Plan", "30 days with dates, topics, real-world scenarios, links to each lesson, statuses and quiz scores."),
        ("Exercise Log", f"{n_ex} exercises (3 difficulty levels) - one row each. Honest statuses ('Passed with hints') tell you what to review."),
        ("Concept Checklist", f"{n_con} concepts with a 1-5 confidence rating. Aim for 4+ on everything by Day 30."),
        ("Projects", "5 milestone projects + 10 portfolio ideas for afterwards."),
        ("Weekly Review", "Auto-calculated weekly stats + reflection questions."),
        ("Time Log", "Optional: minute-by-minute study log with automatic totals."),
        ("Bug Journal", "Write down every compiler message or exception you fix. A chart shows which bugs bite you most."),
        ("Settings", "Change the start date or the lists in the dropdowns."),
        ("Tip", "Excel 365 users: you can also Insert > Checkbox in any blank column. Dropdowns work in every Excel version, Google Sheets and LibreOffice."),
    ]
    for i, (a, b) in enumerate(rows):
        r = 3 + i
        ws_start[f"B{r}"] = a
        ws_start[f"B{r}"].font = Font(bold=True, size=13 if b is None else 11, color=NAVY if b is None else "000000")
        if b:
            ws_start[f"C{r}"] = b
            ws_start[f"C{r}"].alignment = WRAP
            ws_start.row_dimensions[r].height = 34
    ws_start.sheet_properties.tabColor = NAVY
    ws_dash.sheet_properties.tabColor = "70AD47"
    ws_plan.sheet_properties.tabColor = "4472C4"
    ws_set.sheet_properties.tabColor = "7F7F7F"
    wb.active = 1  # open on the Dashboard
    wb.calculation.fullCalcOnLoad = True  # Excel computes every formula when the file opens

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    missing = [n for n in range(1, N_DAYS + 1) if n not in present]
    print(f"Saved {OUT}")
    print(f"  days with a LESSON.md: {len(present)}/{N_DAYS}   exercises: {n_ex}   concepts: {n_con}")
    if missing:
        print("  not written yet (plan rows use the built-in syllabus): " + ", ".join(str(n) for n in missing))


if __name__ == "__main__":
    build()
