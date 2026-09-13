from .auth import authenticate_member, authenticate_admin
from .models import Member, Book


def ask(prompt):
    """Like Python's built-in input(), but sanitizes the result: strips
    ANSI escape sequences and any other non-printable control characters
    that some Windows/Docker terminal setups can leak into stdin --
    especially into the very first input() call right after the
    container starts (e.g. a terminal-size/cursor-position query
    response) -- then trims whitespace. Keeps all normal printable
    characters, including Vietnamese diacritics."""
    import re
    ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')
    raw = input(prompt)
    no_escapes = ANSI_ESCAPE_RE.sub("", raw)
    printable_only = "".join(ch for ch in no_escapes if ch.isprintable())
    return printable_only.strip()


def member_menu(member: Member):
    while True:
        print("\n--- MEMBER MENU ---")
        print("1. View personal information")
        print("2. Search books")
        print("3. View currently borrowed books")
        print("4. View borrow history")
        print("5. View fines")
        print("6. Logout")

        choice = ask("Choose an option: ")

        if choice == "1":
            print(member.view_personal_info())
        elif choice == "2":
            print(Member.search_books(ask("Keyword (title/author/category): ")))
        elif choice == "3":
            print(member.view_borrowed_books())
        elif choice == "4":
            print(member.view_borrow_history())
        elif choice == "5":
            print(member.view_fines())
        elif choice == "6":
            break
        else:
            print("Invalid choice.")


def admin_member_management(admin):
    while True:
        print("\n--- MEMBER MANAGEMENT ---")
        print("1. Add member")
        print("2. Edit member")
        print("3. Delete member")
        print("4. View all members")
        print("5. Back")

        c = ask("Choose: ")

        if c == "1":
            member = Member(
                member_id=ask("Member ID: "),
                username=ask("Username: "),
                password="123456",
                full_name=ask("Full Name: "),
                email=ask("Email: "),
                date_of_birth=ask("Date of Birth (YYYY-MM-DD): "),
                address=ask("Address: "),
                membership_type=ask("Membership Type (Standard/Premium): "),
            )
            admin.add_member(member)
            print("Member added.")

        elif c == "2":
            u = ask("Username: ")
            field = ask("Field (full_name/email/address/membership_type): ")
            value = ask("New value: ")
            admin.update_member(u, {field: value})
            print("Member updated.")

        elif c == "3":
            u = ask("Username: ")
            admin.delete_member(u)
            print("Member deleted.")

        elif c == "4":
            for m in admin.view_member():
                print(f"{m.member_id} - {m.username} - {m.full_name} - {m.email}")

        elif c == "5":
            break


def admin_book_management(admin):
    while True:
        print("\n--- BOOK MANAGEMENT ---")
        print("1. Add book")
        print("2. Edit book")
        print("3. Delete book")
        print("4. View all books")
        print("5. Back")

        c = ask("Choose: ")

        if c == "1":
            qty = int(ask("Quantity: "))
            book = Book(
                code=ask("Book code: "),
                title=ask("Title: "),
                author=ask("Author: "),
                category=ask("Category: "),
                publisher=ask("Publisher: "),
                quantity=qty, available=qty,
            )
            admin.add_book(book)
            print("Book added.")

        elif c == "2":
            code = ask("Book code: ")
            field = ask("Field (title/author/category/publisher/quantity/available): ")
            value = ask("New value: ")
            if field in ("quantity", "available"):
                value = int(value)
            admin.update_book(code, {field: value})
            print("Book updated.")

        elif c == "3":
            code = ask("Book code: ")
            admin.delete_book(code)
            print("Book deleted.")

        elif c == "4":
            for b in admin.view_book():
                print(
                    f"{b.code} - {b.title} - {b.author} - "
                    f"Available: {b.available}/{b.quantity}"
                )

        elif c == "5":
            break


def admin_borrow_management(admin):
    while True:
        print("\n--- BORROW / RETURN MANAGEMENT ---")
        print("1. Borrow book")
        print("2. Return book")
        print("3. View all borrow records")
        print("4. View overdue records")
        print("5. View all fines")
        print("6. Pay a fine")
        print("7. Back")

        c = ask("Choose: ")

        if c == "1":
            print(admin.record_borrow(
                ask("Username: "),
                ask("Book code: "),
                ask("Borrow date (YYYY-MM-DD): "),
                ask("Due date (YYYY-MM-DD): ")
            ))

        elif c == "2":
            print(admin.record_return(
                ask("Record ID: "),
                ask("Return date (YYYY-MM-DD): ")
            ))

        elif c == "3":
            for r in admin.view_borrow_records():
                print(
                    f"{r.record_id} - {r.member_id} - {r.book_code} - "
                    f"Due: {r.due_date} - Status: {r.status}"
                )

        elif c == "4":
            for r in admin.view_overdue_records():
                print(f"{r.record_id} - {r.member_id} - {r.book_code} - Due: {r.due_date} (overdue)")

        elif c == "5":
            for f in admin.view_fines():
                print(f"{f.fine_id} - Record: {f.record_id} - Amount: {f.amount} VND - Status: {f.status}")

        elif c == "6":
            print(admin.pay_fine(ask("Fine ID: ")))

        elif c == "7":
            break


def admin_menu(admin):
    while True:
        print("\n===== ADMIN MAIN MENU =====")
        print("1. Member Management")
        print("2. Book Management")
        print("3. Borrow / Return Management")
        print("4. Logout")

        c = ask("Choose an option: ")

        if c == "1":
            admin_member_management(admin)
        elif c == "2":
            admin_book_management(admin)
        elif c == "3":
            admin_borrow_management(admin)
        elif c == "4":
            break
        else:
            print("Invalid option.")


def run():
    print("Welcome to Library Management System (Group 02)")

    while True:
        role = ask("Login as (member/admin/exit): ")

        if role == "exit":
            break

        if role not in ("member", "admin"):
            print("Invalid role.")
            continue

        username = ask("Username: ")
        password = ask("Password: ")

        if role == "member":
            member = authenticate_member(username, password)
            if member is not None:
                member_menu(member)
            else:
                print("Login failed.")

        else:  # role == "admin"
            admin = authenticate_admin(username, password)
            if admin is not None:
                admin_menu(admin)
            else:
                print("Login failed.")


if __name__ == "__main__":
    run()
