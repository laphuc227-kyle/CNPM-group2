# Library Management System (Group 02)

Object-oriented library management system implemented in Python for
Stage 3 (Implementation) and Stage 4 (Testing) of the project.
Architecture: **Layered** (Presentation / Business / Persistence / Data
-- see the Architectural Design section of the Requirement Specification
document). Available in **two interfaces that share the exact same
Business Layer classes**: a Tkinter desktop GUI (required by the
assignment) and a console app (kept as a lightweight, dependency-free
entry point for quick testing).

## Project Structure
```
app/            Application source code
  db.py           Persistence Layer -- JSON data access (load/save)
  models.py       Business Layer -- domain classes matching the Class
                  Diagram: User -> Member / Administrator (inheritance),
                  Book, BorrowRecord, Fine. All business rules live here
                  (login, search, borrow/return, overdue check, fine
                  calculation) -- nothing in this file talks to the
                  console or the GUI.
  auth.py         Looks up credentials and returns a Member / Administrator
                  object (or None).
  main.py         Presentation Layer -- console menus / entry point
  gui_main.py     Presentation Layer -- GUI entry point (python -m app.gui_main)
  gui/            Presentation Layer -- Tkinter GUI (login_view.py,
                  member_view.py, admin_view.py, dialogs.py, app.py).
                  Every screen calls methods directly on the Member /
                  Administrator objects from models.py -- no business
                  logic is duplicated here.
data/           Sample data (acts as the "database" for this prototype)
tests/          Pytest unit/integration tests (30 automated tests)
docs/           Testing Document.xlsx        29 formal test cases (official 5-column template)
                Task Assignment & Tool Usage Evidence.docx   team's names +
                                                              tool-usage screenshots
                Test_Report.md                test-run summary
                screenshots/                  tool-usage screenshots
```

## Functional Requirements Covered
- Login (member / admin)
- View Personal Information (full name, member ID, email, date of birth,
  address, membership type — read-only)
- Search Books
- View Currently Borrowed Books
- View Fines (fine per overdue book + total outstanding fine,
  5,000 VND/day)
- Member Management (Add / View / Update / Delete) — admin
- Book Management (Add / View / Update / Delete, quantity & availability) — admin
- Borrow / Return Management (record borrow, set due date, record return,
  check whether a returned book is overdue, update availability) — admin

## Object-Oriented Design (matches the Class Diagram)
- `User` (base class) → `Member`, `Administrator` (inheritance)
- `Book`, `BorrowRecord`, `Fine` — each with the attributes and methods
  shown in the Class Diagram (e.g. `Book.check_availability()`,
  `BorrowRecord.check_overdue()`, `Fine.calculate_amount()`)
- `Fine` is a persisted entity — `fine_id`, `record_id`, `amount`, `status`
  (`Unpaid` / `Paid`) — linked 1-to-0..1 with a `BorrowRecord`:
  - A book still borrowed and past its due date shows a **live-calculated**
    fine (no Fine object is persisted yet, since the loan isn't finalized).
  - Returning a book late **creates and persists a Fine** (status `Unpaid`).
    Admin > Borrow/Return Management > "View all fines" / "Pay a fine"
    lets you list and settle these.

## Default accounts
- Admin: `admin` / `admin123`
- Member: `member01` / `123456`

# Run the GUI (required interface)
python -m app.gui_main
(Tkinter ships with standard Python on Windows/Mac -- nothing extra to
install. On some minimal Linux distros you may need: sudo apt install
python3-tk)

# Run the console app
python -m app.main

# Run tests
pytest -vv

# Docker build
docker build -t library-system .

# Docker run (console app; the GUI needs a display and isn't the
# container's default entrypoint)
docker run -it library-system
