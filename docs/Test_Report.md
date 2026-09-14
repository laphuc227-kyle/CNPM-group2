# Test Report – Library Management System (Group 02)

## 1. Overview
- **Project:** Library Management System
- **Test Period:** [start date] – [end date]
- **Tested by:** [names]
- **Reference:** see `Testing Document.xlsx` for the full list of 32 test cases

## 2. Test Scope
- Authentication (member / admin login)
- Member operations (view personal information, search books, view currently
  borrowed books, view borrow history, view fines)
- Member self-registration (create account, reject duplicate username)
- Admin – Member management (add / edit / delete / list, reject duplicate
  username, reject duplicate member ID)
- Admin – Book management (add / edit / delete / list, reject duplicate
  book code)
- Admin – Borrow / Return management (borrow, return, view records, overdue,
  automatic overdue check and fine calculation on return)
- Admin – Fine management (view all fines, pay a fine)
- Unit tests: `tests/test_admin.py`, `tests/test_auth.py`, `tests/test_member.py`
- Manual tests: console menu walkthrough (see `Testing Document.xlsx`, TC01–TC32)

## 3. Test Summary

| Metric | Count |
|---|---|
| Total automated tests | 35 |
| Passed | 35 |
| Failed | 0 |
| Blocked | 0 |
| Pending | 0 |

All 35 automated tests pass against a freshly-seeded `data/sample_data.json`
(1 member, 2 books, 1 active borrow record, no fines — see the file for the
exact seed). Manual test cases TC01–TC32 in `Testing Document.xlsx` were
walked through against the running program (`python -m app.main`) and match
the documented Expected Results.

> **Note on re-running tests:** the test suite reads/writes the same
> `data/sample_data.json` file the app uses (there is no separate test
> database/fixture reset). Running `pytest` mutates this file, so running it
> a second time in a row against the now-modified file can produce
> unrelated failures. Always restore the seed file before re-running the
> suite, e.g. `git checkout -- data/sample_data.json` (if using Git) or
> re-copy it from a backup. This is a known limitation, not a code bug —
> see Section 6.

## 4. Automated Test Results
```
$ pytest -vv

tests/test_admin.py::test_add_member PASSED
tests/test_admin.py::test_add_member_rejects_duplicate_username PASSED
tests/test_admin.py::test_add_member_rejects_duplicate_member_id PASSED
tests/test_admin.py::test_edit_member PASSED
tests/test_admin.py::test_delete_member PASSED
tests/test_admin.py::test_add_book PASSED
tests/test_admin.py::test_add_book_rejects_duplicate_code PASSED
tests/test_admin.py::test_edit_book PASSED
tests/test_admin.py::test_borrow_book_success PASSED
tests/test_admin.py::test_return_book_on_time_has_no_fine PASSED
tests/test_admin.py::test_borrow_and_return_late_calculates_fine PASSED
tests/test_admin.py::test_late_return_persists_a_fine_record PASSED
tests/test_admin.py::test_pay_fine_marks_it_paid PASSED
tests/test_admin.py::test_pay_fine_not_found PASSED
tests/test_admin.py::test_borrow_book_no_copies_available PASSED
tests/test_admin.py::test_return_book_record_not_found PASSED
tests/test_admin.py::test_list_overdue_records_includes_still_borrowed_past_due PASSED
tests/test_admin.py::test_delete_book PASSED
tests/test_admin.py::test_borrow_book_member_not_found PASSED
tests/test_admin.py::test_borrow_book_stores_member_id_not_username PASSED
tests/test_auth.py::test_member_login_success PASSED
tests/test_auth.py::test_member_login_fail PASSED
tests/test_auth.py::test_admin_login_success PASSED
tests/test_auth.py::test_admin_login_fail PASSED
tests/test_auth.py::test_register_creates_a_working_login PASSED
tests/test_auth.py::test_register_rejects_duplicate_username PASSED
tests/test_member.py::test_get_member_found PASSED
tests/test_member.py::test_get_member_not_found PASSED
tests/test_member.py::test_view_personal_info PASSED
tests/test_member.py::test_search_books_found PASSED
tests/test_member.py::test_search_books_not_found PASSED
tests/test_member.py::test_view_borrowed_books PASSED
tests/test_member.py::test_view_borrow_history PASSED
tests/test_member.py::test_view_fines_shows_outstanding_fine_for_overdue_book PASSED
tests/test_member.py::test_view_fines_shows_persisted_fine_for_returned_late_book PASSED

========================= 35 passed in 0.07s =========================
```

## 5. Bugs Found

| Bug ID | Module | Description | Severity | Status | Fixed in |
|---|---|---|---|---|---|
| BUG-01 | `models.Administrator.record_return` | Overdue check compared the book's due date against **today's system date** instead of the **actual return date** entered by the admin. This gave the wrong result whenever an admin recorded a return that happened in the past (a very common real scenario). | High | Fixed | `app/models.py` — `BorrowRecord.check_overdue()` / `Fine.calculate_amount()` now take an explicit `reference_date` (the return date), instead of defaulting to `date.today()`. |
| BUG-02 | `data/sample_data.json` (submission hygiene, not application code) | The data file shipped in an earlier build had been overwritten by a leftover test/manual-run session: it contained borrow records referencing book codes (`BK998`, `BK999`) that do not exist in the `books` list, and a fine already marked `Paid` that the test suite expects to be `Unpaid`. This caused 4 automated tests to fail when re-run and made `view_borrowed_books` output nonsensical entries. | Medium | Fixed | `data/sample_data.json` reset to the intended seed (1 member, 2 books, 1 active borrow record `BR001`, no fines). |
| BUG-03 | `models.Administrator.add_member` / `add_book` | No duplicate check: an admin could add a member with a username or member ID that already existed, or a book with a code that already existed, silently creating conflicting/overwritten-looking records. | High | Fixed | `add_member()` now rejects a duplicate username or member ID; `add_book()` now rejects a duplicate book code. Both raise `ValueError`, caught and shown as an error message in the console app and the GUI. |

## 5b. New Feature Added

| Feature | Description |
|---|---|
| Member self-registration | A new "Register" option at the login screen (console: `register`; GUI: "New here? Create a member account" button) lets a person create their own Member account without an admin, via `Member.register()` / `auth.register_member()`. Rejects a username that is already taken; on success, the new account is logged in immediately. |

No other defects were found during this test cycle; all 30 automated tests
and all 32 manual test cases in `Testing Document.xlsx` pass against the
current build with a freshly-seeded data file.

## 6. Conclusion
The Library Management System meets all the functional requirements
covered in this test cycle: authentication, member self-service (personal
info, book search, borrowed books, borrow history, fines), member
self-registration, and admin management of members, books,
borrowing/returning, and fines — including automatic overdue detection
and fine calculation on return (matching the Class Diagram's `Fine`
entity design: persisted `fine_id` / `record_id` / `amount` / `status`),
and duplicate-prevention checks on member username, member ID, and book
code.

The system is ready for demonstration/submission. Known limitations for a
future iteration: the console interface has no input validation for
malformed dates (e.g. wrong `YYYY-MM-DD` format) beyond what Python's
`datetime.strptime` rejects with a raw traceback; there is no persistence
layer beyond a single local JSON file (no concurrent-user support); and,
as noted in Section 3, the test suite is not self-isolating -- it shares
`data/sample_data.json` with the running app instead of using a separate
fixture/temp file, so the seed file must be restored before each re-run.
