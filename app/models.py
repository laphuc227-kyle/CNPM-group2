"""Domain classes for the Library Management System, matching the
Class Diagram from Stage 1/2: User -> Member / Administrator
(inheritance), Book, BorrowRecord, Fine.

This module is the Business Layer in the system's Layered Architecture
(see the Architectural Design section of the Requirement Specification
document): it depends only on the Persistence Layer (db.py) and knows
nothing about the Presentation Layer (console app/main.py or the
Tkinter app/gui/ package).
"""
from datetime import date, datetime

from .db import load_data, save_data

FINE_PER_DAY = 5000  # VND, charged for each day a book is overdue


def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _coerce_date(value):
    """Accepts a date object, a 'YYYY-MM-DD' string, or None."""
    if value is None:
        return None
    if isinstance(value, str):
        return _parse_date(value)
    return value


def _find_member_dict(data, username):
    for m in data["members"]:
        if m["username"] == username:
            return m
    return None


def _find_book_dict(data, code):
    for b in data["books"]:
        if b["code"] == code:
            return b
    return None


# ==========================================================================
# User (base class)
# ==========================================================================

class User:
    """Base class for any account that can log in."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self, username, password):
        return self.username == username and self.password == password


# ==========================================================================
# Member
# ==========================================================================

class Member(User):
    """A library member. Wraps one row of the Members table and provides
    every member self-service function."""

    def __init__(self, member_id, username, password, full_name, email,
                 date_of_birth, address, membership_type):
        super().__init__(username, password)
        self.member_id = member_id
        self.full_name = full_name
        self.email = email
        self.date_of_birth = date_of_birth
        self.address = address
        self.membership_type = membership_type

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["member_id"], d["username"], d["password"], d["full_name"],
            d["email"], d["date_of_birth"], d["address"], d["membership_type"]
        )

    def to_dict(self):
        return {
            "member_id": self.member_id, "username": self.username,
            "password": self.password, "full_name": self.full_name,
            "email": self.email, "date_of_birth": self.date_of_birth,
            "address": self.address, "membership_type": self.membership_type,
        }

    # ---------- Self-registration ----------

    @staticmethod
    def _next_member_id(data):
        if not data["members"]:
            return "LIB001"
        last = max(int(m["member_id"][3:]) for m in data["members"])
        return f"LIB{last + 1:03d}"

    @classmethod
    def register(cls, username, password, full_name, email, date_of_birth,
                 address, membership_type="Standard"):
        """Self-registration: a new person creates their own Member
        account directly (as opposed to Administrator.add_member(),
        which is an admin adding someone on their behalf). Rejects a
        username that is already taken; otherwise generates a new
        member_id and persists the new Member, matching the Member
        entity in the Class Diagram exactly.
        """
        data = load_data()
        if _find_member_dict(data, username) is not None:
            raise ValueError(f"Username '{username}' is already taken.")

        member = cls(
            member_id=cls._next_member_id(data), username=username, password=password,
            full_name=full_name, email=email, date_of_birth=date_of_birth,
            address=address, membership_type=membership_type,
        )
        data["members"].append(member.to_dict())
        save_data(data)
        return member

    # ---------- Member self-service functions ----------

    def view_personal_info(self):
        return (
            f"Full Name: {self.full_name}\n"
            f"Member ID: {self.member_id}\n"
            f"Email: {self.email}\n"
            f"Date of Birth: {self.date_of_birth}\n"
            f"Address: {self.address}\n"
            f"Membership Type: {self.membership_type}"
        )

    @staticmethod
    def search_books(keyword):
        data = load_data()
        keyword = keyword.lower()
        results = [
            b for b in data["books"]
            if keyword in b["title"].lower()
            or keyword in b["author"].lower()
            or keyword in b["category"].lower()
        ]
        if not results:
            return "No books found."
        lines = ["Search Results:"]
        for b in results:
            lines.append(
                f"- {b['code']} | {b['title']} | {b['author']} | "
                f"Available: {b['available']}/{b['quantity']}"
            )
        return "\n".join(lines)

    def view_borrowed_books(self):
        data = load_data()
        records = [
            r for r in data["borrow_records"]
            if r["member_id"] == self.member_id and r["return_date"] is None
        ]
        if not records:
            return "You have no books currently borrowed."
        lines = ["Currently Borrowed Books:"]
        for r in records:
            book = _find_book_dict(data, r["book_code"])
            title = book["title"] if book else r["book_code"]
            author = book["author"] if book else "-"
            lines.append(f"- {title} | Author: {author} | Due: {r['due_date']}")
        return "\n".join(lines)

    def view_borrow_history(self):
        data = load_data()
        records = [r for r in data["borrow_records"] if r["member_id"] == self.member_id]
        if not records:
            return "No borrow history found."
        lines = ["Borrow History:"]
        for r in records:
            book = _find_book_dict(data, r["book_code"])
            title = book["title"] if book else r["book_code"]
            returned = r["return_date"] if r["return_date"] else "-"
            lines.append(
                f"- {title} | Borrowed: {r['borrow_date']} | "
                f"Due: {r['due_date']} | Returned: {returned} | Status: {r['status']}"
            )
        return "\n".join(lines)

    def view_fines(self):
        """Displays the outstanding fine for each overdue book, plus the
        total: books still borrowed and past due are calculated live
        (no Fine record exists yet); books already returned late show
        the persisted, unpaid Fine record created at return time."""
        data = load_data()
        records = [r for r in data["borrow_records"] if r["member_id"] == self.member_id]

        lines = []
        total = 0
        for r in records:
            book = _find_book_dict(data, r["book_code"])
            title = book["title"] if book else r["book_code"]
            record = BorrowRecord.from_dict(r)

            if r["return_date"] is None:
                overdue_days = record.check_overdue()
                if overdue_days > 0:
                    amount = Fine.calculate_amount(r["due_date"])
                    total += amount
                    lines.append(
                        f"- {title} | Overdue: {overdue_days} day(s) | "
                        f"Fine: {amount} VND (ongoing, not yet returned)"
                    )
            else:
                fine = Fine.find_for_record(r["record_id"], data)
                if fine is not None and fine.status == "Unpaid":
                    total += fine.amount
                    lines.append(
                        f"- {title} | Fine: {fine.amount} VND "
                        f"(Fine ID: {fine.fine_id}, Unpaid)"
                    )

        if not lines:
            return "No outstanding fines."
        lines.append(f"Total Fine: {total} VND")
        return "Fines:\n" + "\n".join(lines)


# ==========================================================================
# Book
# ==========================================================================

class Book:
    def __init__(self, code, title, author, category, publisher, quantity, available):
        self.code = code
        self.title = title
        self.author = author
        self.category = category
        self.publisher = publisher
        self.quantity = quantity
        self.available = available

    @classmethod
    def from_dict(cls, d):
        return cls(d["code"], d["title"], d["author"], d["category"],
                    d["publisher"], d["quantity"], d["available"])

    def to_dict(self):
        return {
            "code": self.code, "title": self.title, "author": self.author,
            "category": self.category, "publisher": self.publisher,
            "quantity": self.quantity, "available": self.available,
        }

    def check_availability(self):
        return self.available > 0

    def update_quantity(self, delta):
        """Adjusts the available-copy count by delta (-1 on borrow, +1 on return)."""
        self.available += delta


# ==========================================================================
# BorrowRecord
# ==========================================================================

class BorrowRecord:
    def __init__(self, record_id, member_id, book_code, borrow_date, due_date,
                 return_date=None, status="Borrowed"):
        self.record_id = record_id
        self.member_id = member_id
        self.book_code = book_code
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.return_date = return_date
        self.status = status

    @classmethod
    def from_dict(cls, d):
        return cls(d["record_id"], d["member_id"], d["book_code"],
                    d["borrow_date"], d["due_date"], d["return_date"], d["status"])

    def to_dict(self):
        return {
            "record_id": self.record_id, "member_id": self.member_id,
            "book_code": self.book_code, "borrow_date": self.borrow_date,
            "due_date": self.due_date, "return_date": self.return_date,
            "status": self.status,
        }

    def check_overdue(self, reference_date=None):
        """Number of days overdue. Compares against reference_date if
        given; otherwise against this record's own return_date if
        already returned, or today if still active. Returns 0 if not
        overdue."""
        due = _parse_date(self.due_date)
        if reference_date is not None:
            ref = _coerce_date(reference_date)
        elif self.return_date is not None:
            ref = _parse_date(self.return_date)
        else:
            ref = date.today()
        return max((ref - due).days, 0)

    def record_return(self, return_date):
        """Marks this record returned on return_date and updates status.
        Returns the number of overdue days (0 if returned on time)."""
        self.return_date = return_date
        overdue_days = self.check_overdue(reference_date=return_date)
        self.status = "Returned (Overdue)" if overdue_days > 0 else "Returned"
        return overdue_days


# ==========================================================================
# Fine
# ==========================================================================

class Fine:
    def __init__(self, fine_id, record_id, amount, status="Unpaid"):
        self.fine_id = fine_id
        self.record_id = record_id
        self.amount = amount
        self.status = status

    @classmethod
    def from_dict(cls, d):
        return cls(d["fine_id"], d["record_id"], d["amount"], d["status"])

    def to_dict(self):
        return {"fine_id": self.fine_id, "record_id": self.record_id,
                "amount": self.amount, "status": self.status}

    @staticmethod
    def calculate_amount(due_date, reference_date=None):
        due = _parse_date(due_date)
        ref = _coerce_date(reference_date) or date.today()
        days = max((ref - due).days, 0)
        return days * FINE_PER_DAY

    @staticmethod
    def find_for_record(record_id, data=None):
        data = data if data is not None else load_data()
        for f in data["fines"]:
            if f["record_id"] == record_id:
                return Fine.from_dict(f)
        return None

    def pay(self):
        self.status = "Paid"


# ==========================================================================
# Administrator
# ==========================================================================

class Administrator(User):
    """A librarian/admin account. Orchestrates CRUD on Members and Books
    and manages the borrow/return workflow, matching the Class Diagram."""

    def __init__(self, username="admin", password="admin123"):
        super().__init__(username, password)

    # ---------- Member Management ----------

    def add_member(self, member: Member):
        """Raises ValueError if the username or the member_id is already
        taken -- an admin enters member_id by hand (unlike self-service
        Member.register(), which generates it), so it can collide too."""
        data = load_data()
        if _find_member_dict(data, member.username) is not None:
            raise ValueError(f"Username '{member.username}' is already taken.")
        if any(m["member_id"] == member.member_id for m in data["members"]):
            raise ValueError(f"Member ID '{member.member_id}' already exists.")
        data["members"].append(member.to_dict())
        save_data(data)

    def update_member(self, username, changes):
        data = load_data()
        m = _find_member_dict(data, username)
        if m is not None:
            m.update(changes)
            save_data(data)

    def delete_member(self, username):
        data = load_data()
        data["members"] = [m for m in data["members"] if m["username"] != username]
        save_data(data)

    def view_member(self):
        data = load_data()
        return [Member.from_dict(m) for m in data["members"]]

    # ---------- Book Management ----------

    def add_book(self, book: Book):
        """Raises ValueError if the book code is already used -- same
        rule as Member usernames, so the library can't end up with two
        different books sharing one code."""
        data = load_data()
        if _find_book_dict(data, book.code) is not None:
            raise ValueError(f"Book code '{book.code}' already exists.")
        data["books"].append(book.to_dict())
        save_data(data)

    def update_book(self, code, changes):
        data = load_data()
        b = _find_book_dict(data, code)
        if b is not None:
            b.update(changes)
            save_data(data)

    def delete_book(self, code):
        data = load_data()
        data["books"] = [b for b in data["books"] if b["code"] != code]
        save_data(data)

    def view_book(self):
        data = load_data()
        return [Book.from_dict(b) for b in data["books"]]

    # ---------- Borrow / Return Management ----------

    @staticmethod
    def _next_record_id(data):
        if not data["borrow_records"]:
            return "BR001"
        last = max(int(r["record_id"][2:]) for r in data["borrow_records"])
        return f"BR{last + 1:03d}"

    @staticmethod
    def _next_fine_id(data):
        if not data["fines"]:
            return "FN001"
        last = max(int(f["fine_id"][2:]) for f in data["fines"])
        return f"FN{last + 1:03d}"

    def record_borrow(self, username, book_code, borrow_date, due_date):
        """The admin enters the member's username (for convenience -- the
        same field used at login), but the system looks up and stores
        member_id -- the real foreign key referencing Members.member_id
        (the primary key) -- inside the new BorrowRecord."""
        data = load_data()

        member_dict = _find_member_dict(data, username)
        if member_dict is None:
            return "Member not found."

        book_dict = _find_book_dict(data, book_code)
        if book_dict is None:
            return "Book not found."

        book = Book.from_dict(book_dict)
        if not book.check_availability():
            return "No copies available."

        book.update_quantity(-1)
        book_dict["available"] = book.available

        record = BorrowRecord(
            record_id=self._next_record_id(data),
            member_id=member_dict["member_id"], book_code=book_code,
            borrow_date=borrow_date, due_date=due_date,
        )
        data["borrow_records"].append(record.to_dict())
        save_data(data)
        return f"Book borrowed. Record ID: {record.record_id}"

    def record_return(self, record_id, return_date):
        """Records a return, checks whether it was overdue, updates book
        availability, and -- if late -- creates a persisted Fine."""
        data = load_data()
        for r in data["borrow_records"]:
            if r["record_id"] == record_id and r["return_date"] is None:
                record = BorrowRecord.from_dict(r)
                overdue_days = record.record_return(return_date)
                r["return_date"] = record.return_date
                r["status"] = record.status

                book_dict = _find_book_dict(data, r["book_code"])
                if book_dict is not None:
                    book = Book.from_dict(book_dict)
                    book.update_quantity(1)
                    book_dict["available"] = book.available
                save_data(data)

                if overdue_days > 0:
                    amount = Fine.calculate_amount(r["due_date"], reference_date=return_date)
                    fine = self._create_fine(record_id, amount)
                    return (
                        f"Book returned. This book was {overdue_days} day(s) "
                        f"overdue. Fine: {fine.amount} VND "
                        f"(Fine ID: {fine.fine_id}, Status: {fine.status})"
                    )
                return "Book returned."
        return "Active borrow record not found."

    def _create_fine(self, record_id, amount):
        """Creates and persists a Fine for a finalized (returned-late)
        borrow record. Returns the existing Fine instead of duplicating
        one if it already exists (keeps the 0..1 rule)."""
        data = load_data()
        existing = Fine.find_for_record(record_id, data)
        if existing is not None:
            return existing
        fine = Fine(self._next_fine_id(data), record_id, amount, "Unpaid")
        data["fines"].append(fine.to_dict())
        save_data(data)
        return fine

    def view_borrow_records(self):
        data = load_data()
        return [BorrowRecord.from_dict(r) for r in data["borrow_records"]]

    def view_overdue_records(self):
        """Records still borrowed (not yet returned) and past their due date."""
        data = load_data()
        result = []
        for r in data["borrow_records"]:
            if r["return_date"] is None:
                record = BorrowRecord.from_dict(r)
                if record.check_overdue() > 0:
                    result.append(record)
        return result

    def view_fines(self):
        data = load_data()
        return [Fine.from_dict(f) for f in data["fines"]]

    def pay_fine(self, fine_id):
        data = load_data()
        for f in data["fines"]:
            if f["fine_id"] == fine_id:
                f["status"] = "Paid"
                save_data(data)
                return "Fine marked as paid."
        return "Fine not found."
