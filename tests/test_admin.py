from app.models import Administrator, Member, Book
from app.db import load_data

admin = Administrator()


def test_add_member():
    new_member = Member(
        member_id="LIB999", username="user999", password="123456",
        full_name="Test User", email="test@ut.edu.vn",
        date_of_birth="2000-01-01", address="Test Address",
        membership_type="Standard",
    )
    admin.add_member(new_member)
    data = load_data()

    assert any(m["username"] == "user999" for m in data["members"])


def test_edit_member():
    admin.update_member("user999", {"address": "New Address"})
    data = load_data()
    updated = next(m for m in data["members"] if m["username"] == "user999")

    assert updated["address"] == "New Address"


def test_delete_member():
    admin.delete_member("user999")
    data = load_data()

    assert not any(m["username"] == "user999" for m in data["members"])


def test_add_book():
    admin.add_book(Book(
        code="BK999", title="Test Book", author="Test Author",
        category="Test", publisher="Test Publisher", quantity=2, available=2,
    ))
    data = load_data()

    assert any(b["code"] == "BK999" for b in data["books"])


def test_edit_book():
    admin.update_book("BK999", {"title": "Updated Test Book"})
    data = load_data()
    updated = next(b for b in data["books"] if b["code"] == "BK999")

    assert updated["title"] == "Updated Test Book"


def test_borrow_book_success():
    result = admin.record_borrow("member01", "BK999", "2026-08-01", "2026-08-08")
    data = load_data()
    book = next(b for b in data["books"] if b["code"] == "BK999")
    record = next(
        r for r in data["borrow_records"]
        if r["book_code"] == "BK999" and r["return_date"] is None
    )

    assert "Book borrowed" in result
    assert book["available"] == 1
    assert record["status"] == "Borrowed"


def test_return_book_on_time_has_no_fine():
    data = load_data()
    record = next(
        r for r in data["borrow_records"]
        if r["book_code"] == "BK999" and r["return_date"] is None
    )

    # Returned exactly on the due date -> not overdue.
    result = admin.record_return(record["record_id"], "2026-08-08")
    data = load_data()
    book = next(b for b in data["books"] if b["code"] == "BK999")
    updated_record = next(
        r for r in data["borrow_records"] if r["record_id"] == record["record_id"]
    )

    assert result == "Book returned."
    assert book["available"] == 2
    assert updated_record["status"] == "Returned"


def test_borrow_and_return_late_calculates_fine():
    borrow_result = admin.record_borrow("member01", "BK999", "2026-08-10", "2026-08-15")
    data = load_data()
    record = next(
        r for r in data["borrow_records"]
        if r["book_code"] == "BK999" and r["return_date"] is None
    )
    assert "Book borrowed" in borrow_result

    # Returned 5 days late -> fine = 5 * 5000 = 25000 VND.
    result = admin.record_return(record["record_id"], "2026-08-20")
    data = load_data()
    updated_record = next(
        r for r in data["borrow_records"] if r["record_id"] == record["record_id"]
    )

    assert "5 day(s) overdue" in result
    assert "25000 VND" in result
    assert updated_record["status"] == "Returned (Overdue)"


def test_late_return_persists_a_fine_record():
    # test_borrow_and_return_late_calculates_fine (above) already created
    # a Fine record for this BK999 return. It must be stored, Unpaid,
    # for exactly this amount.
    fines = admin.view_fines()
    fine = next((f for f in fines if f.amount == 25000), None)

    assert fine is not None
    assert fine.status == "Unpaid"


def test_pay_fine_marks_it_paid():
    fines = admin.view_fines()
    fine = next(f for f in fines if f.amount == 25000)

    result = admin.pay_fine(fine.fine_id)
    updated = next(f for f in admin.view_fines() if f.fine_id == fine.fine_id)

    assert result == "Fine marked as paid."
    assert updated.status == "Paid"


def test_pay_fine_not_found():
    result = admin.pay_fine("FN_NOT_EXIST")
    assert result == "Fine not found."


def test_borrow_book_no_copies_available():
    # BK999 has 2 copies; borrow both (without returning) to exhaust stock,
    # then the next borrow attempt must be rejected.
    admin.record_borrow("member01", "BK999", "2026-08-18", "2026-09-01")
    admin.record_borrow("member01", "BK999", "2026-08-18", "2026-09-01")
    result = admin.record_borrow("member01", "BK999", "2026-08-18", "2026-09-01")
    assert result == "No copies available."


def test_return_book_record_not_found():
    result = admin.record_return("BR_NOT_EXIST", "2026-08-20")
    assert result == "Active borrow record not found."


def test_list_overdue_records_includes_still_borrowed_past_due():
    # BR001 (seeded, member01, BK001, due 2026-08-10) is still borrowed
    # and its due date is in the past -> must appear in overdue records.
    overdue = admin.view_overdue_records()
    assert any(r.record_id == "BR001" for r in overdue)


def test_delete_book():
    admin.delete_book("BK999")
    data = load_data()

    assert not any(b["code"] == "BK999" for b in data["books"])


def test_borrow_book_member_not_found():
    result = admin.record_borrow("no_such_user", "BK001", "2026-08-18", "2026-09-01")
    assert result == "Member not found."


def test_borrow_book_stores_member_id_not_username():
    # The FK stored in BorrowRecords must be member_id (the real PK of
    # Members), not the username, per the corrected Data Model.
    admin.add_book(Book(
        code="BK998", title="FK Check Book", author="Test Author",
        category="Test", publisher="Test Publisher", quantity=1, available=1,
    ))
    admin.record_borrow("member01", "BK998", "2026-08-18", "2026-09-01")
    data = load_data()
    record = next(r for r in data["borrow_records"] if r["book_code"] == "BK998")

    assert record["member_id"] == "LIB001"
    assert "username" not in record

    admin.delete_book("BK998")
