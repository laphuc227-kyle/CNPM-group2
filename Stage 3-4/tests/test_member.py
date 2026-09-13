from app.auth import authenticate_member
from app.models import Member


def test_get_member_found():
    m = authenticate_member("member01", "123456")
    assert m is not None
    assert m.full_name == "Nguyen Van A"


def test_get_member_not_found():
    assert authenticate_member("no_such_user", "whatever") is None


def test_view_personal_info():
    m = authenticate_member("member01", "123456")
    info = m.view_personal_info()
    assert "Nguyen Van A" in info
    assert "LIB001" in info
    assert "Standard" in info


def test_search_books_found():
    result = Member.search_books("clean")
    assert "BK001" in result
    assert "Clean Code" in result


def test_search_books_not_found():
    result = Member.search_books("nonexistenttitle")
    assert result == "No books found."


def test_view_borrowed_books():
    # BR001 (BK001, due 2026-08-10) is seeded as still borrowed by member01.
    m = authenticate_member("member01", "123456")
    result = m.view_borrowed_books()
    assert "Clean Code" in result
    assert "Due: 2026-08-10" in result


def test_view_borrow_history():
    m = authenticate_member("member01", "123456")
    result = m.view_borrow_history()
    assert "Clean Code" in result


def test_view_fines_shows_outstanding_fine_for_overdue_book():
    # BR001's due date (2026-08-10) is in the past and the book has not
    # been returned, so it must show up as an outstanding fine.
    m = authenticate_member("member01", "123456")
    result = m.view_fines()
    assert "Clean Code" in result
    assert "Fine" in result
    assert "Total Fine" in result


def test_view_fines_shows_persisted_fine_for_returned_late_book():
    # Return BR001 (due 2026-08-10) 5 days late -> creates a persisted
    # Fine record, which must then show up here as Unpaid.
    from app.models import Administrator
    admin = Administrator()
    result_before = admin.record_return("BR001", "2026-08-15")
    assert "5 day(s) overdue" in result_before

    m = authenticate_member("member01", "123456")
    result = m.view_fines()
    assert "Clean Code" in result
    assert "Unpaid" in result
    assert "25000 VND" in result
