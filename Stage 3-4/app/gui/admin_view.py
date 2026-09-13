import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from ..models import Administrator, Member, Book
from .dialogs import ask_multi_field


class AdminView(ttk.Frame):
    """Admin dashboard: sidebar with Members / Books / Borrow-Return, each
    backed directly by the same Administrator methods (models.py) the
    console's admin menu calls. No new business logic is introduced here."""

    def __init__(self, parent, admin: Administrator, on_logout):
        super().__init__(parent)
        self.admin = admin
        self.on_logout = on_logout

        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=232)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ttk.Label(
            sidebar, text="ADMIN MENU", background="#f2f2f2",
            foreground="#888888", padding=(12, 12, 12, 4)
        ).pack(fill="x")

        for label, cmd in [
            ("Members", self.show_members),
            ("Books", self.show_books),
            ("Borrow / Return", self.show_borrow_return),
        ]:
            ttk.Button(
                sidebar, text=label, style="SidebarItem.TButton", command=cmd
            ).pack(fill="x")

        ttk.Frame(sidebar).pack(fill="y", expand=True)
        ttk.Button(
            sidebar, text="Logout", style="SidebarItem.TButton",
            command=self.on_logout
        ).pack(fill="x", side="bottom", pady=(0, 8))

        self.content = ttk.Frame(self, padding=16)
        self.content.pack(side="left", fill="both", expand=True)

        self.show_members()

    # ---------- helpers ----------

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _header(self, title, buttons):
        row = ttk.Frame(self.content)
        row.pack(fill="x", pady=(0, 10))
        ttk.Label(row, text=title, style="Heading.TLabel").pack(side="left")
        btn_row = ttk.Frame(row)
        btn_row.pack(side="right")
        for text, cmd in buttons:
            ttk.Button(btn_row, text=text, command=cmd).pack(side="left", padx=(6, 0))

    def _make_table(self, columns):
        frame = ttk.Frame(self.content)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="w")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return tree

    # ---------- Members ----------

    def show_members(self):
        self._clear_content()
        self._header("Members", [
            ("Add member", self._add_member),
            ("Edit member", self._edit_member),
            ("Delete member", self._delete_member),
            ("Refresh", self.show_members),
        ])
        tree = self._make_table(
            ["member_id", "username", "full_name", "email", "membership_type"]
        )
        for m in self.admin.view_member():
            tree.insert("", "end", values=(
                m.member_id, m.username, m.full_name, m.email, m.membership_type,
            ))

    def _add_member(self):
        values = ask_multi_field(self, "Add member", [
            ("Member ID", "member_id"),
            ("Username", "username"),
            ("Password", "password"),
            ("Full name", "full_name"),
            ("Email", "email"),
            ("Date of birth (YYYY-MM-DD)", "date_of_birth"),
            ("Address", "address"),
            ("Membership type", "membership_type"),
        ])
        if values is None:
            return
        if not values["member_id"] or not values["username"]:
            messagebox.showerror("Add member", "Member ID and Username are required.")
            return
        member = Member(
            member_id=values["member_id"], username=values["username"],
            password=values["password"] or "123456", full_name=values["full_name"],
            email=values["email"], date_of_birth=values["date_of_birth"],
            address=values["address"], membership_type=values["membership_type"],
        )
        self.admin.add_member(member)
        self.show_members()

    def _edit_member(self):
        username = simpledialog.askstring("Edit member", "Username of the member to edit:", parent=self)
        if not username:
            return
        field = simpledialog.askstring(
            "Edit member",
            "Field to change (full_name / email / date_of_birth / address / membership_type):",
            parent=self,
        )
        if not field:
            return
        new_value = simpledialog.askstring("Edit member", f"New value for '{field}':", parent=self)
        if new_value is None:
            return
        self.admin.update_member(username, {field: new_value})
        self.show_members()

    def _delete_member(self):
        username = simpledialog.askstring("Delete member", "Username of the member to delete:", parent=self)
        if not username:
            return
        if messagebox.askyesno("Delete member", f"Delete member '{username}'?"):
            self.admin.delete_member(username)
            self.show_members()

    # ---------- Books ----------

    def show_books(self):
        self._clear_content()
        self._header("Books", [
            ("Add book", self._add_book),
            ("Edit book", self._edit_book),
            ("Delete book", self._delete_book),
            ("Refresh", self.show_books),
        ])
        tree = self._make_table(
            ["code", "title", "author", "category", "quantity", "available"]
        )
        for b in self.admin.view_book():
            tree.insert("", "end", values=(
                b.code, b.title, b.author, b.category, b.quantity, b.available,
            ))

    def _add_book(self):
        values = ask_multi_field(self, "Add book", [
            ("Code", "code"),
            ("Title", "title"),
            ("Author", "author"),
            ("Category", "category"),
            ("Publisher", "publisher"),
            ("Quantity", "quantity"),
        ])
        if values is None:
            return
        if not values["code"] or not values["title"]:
            messagebox.showerror("Add book", "Code and Title are required.")
            return
        try:
            qty = int(values["quantity"])
        except ValueError:
            messagebox.showerror("Add book", "Quantity must be a number.")
            return
        book = Book(
            code=values["code"], title=values["title"], author=values["author"],
            category=values["category"], publisher=values["publisher"],
            quantity=qty, available=qty,
        )
        self.admin.add_book(book)
        self.show_books()

    def _edit_book(self):
        code = simpledialog.askstring("Edit book", "Book code to edit:", parent=self)
        if not code:
            return
        field = simpledialog.askstring(
            "Edit book",
            "Field to change (title / author / category / publisher / quantity / available):",
            parent=self,
        )
        if not field:
            return
        new_value = simpledialog.askstring("Edit book", f"New value for '{field}':", parent=self)
        if new_value is None:
            return
        if field in ("quantity", "available"):
            try:
                new_value = int(new_value)
            except ValueError:
                messagebox.showerror("Edit book", f"'{field}' must be a number.")
                return
        self.admin.update_book(code, {field: new_value})
        self.show_books()

    def _delete_book(self):
        code = simpledialog.askstring("Delete book", "Book code to delete:", parent=self)
        if not code:
            return
        if messagebox.askyesno("Delete book", f"Delete book '{code}'?"):
            self.admin.delete_book(code)
            self.show_books()

    # ---------- Borrow / Return ----------

    def show_borrow_return(self):
        self._clear_content()
        self._header("Borrow / Return Management", [
            ("Borrow book", self._borrow_book),
            ("Return book", self._return_book),
            ("Pay a fine", self._pay_fine),
        ])

        actions = ttk.Frame(self.content)
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="View all records", command=self._view_records).pack(side="left")
        ttk.Button(actions, text="View overdue records", command=self._view_overdue).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="View all fines", command=self._view_fines).pack(side="left", padx=(8, 0))

        self.table_area = ttk.Frame(self.content)
        self.table_area.pack(fill="both", expand=True)
        self._view_records()

    def _make_table_in(self, parent, columns):
        for w in parent.winfo_children():
            w.destroy()
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="w")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return tree

    def _view_records(self):
        tree = self._make_table_in(
            self.table_area,
            ["record_id", "member_id", "book_code", "due_date", "status"]
        )
        for r in self.admin.view_borrow_records():
            tree.insert("", "end", values=(
                r.record_id, r.member_id, r.book_code, r.due_date, r.status,
            ))

    def _view_overdue(self):
        tree = self._make_table_in(
            self.table_area,
            ["record_id", "member_id", "book_code", "due_date"]
        )
        for r in self.admin.view_overdue_records():
            tree.insert("", "end", values=(
                r.record_id, r.member_id, r.book_code, r.due_date,
            ))

    def _view_fines(self):
        tree = self._make_table_in(
            self.table_area,
            ["fine_id", "record_id", "amount", "status"]
        )
        for f in self.admin.view_fines():
            tree.insert("", "end", values=(
                f.fine_id, f.record_id, f.amount, f.status,
            ))

    def _borrow_book(self):
        values = ask_multi_field(self, "Borrow book", [
            ("Username", "username"),
            ("Book code", "book_code"),
            ("Borrow date (YYYY-MM-DD)", "borrow_date"),
            ("Due date (YYYY-MM-DD)", "due_date"),
        ])
        if values is None:
            return
        message = self.admin.record_borrow(
            values["username"], values["book_code"],
            values["borrow_date"], values["due_date"]
        )
        messagebox.showinfo("Borrow book", message)
        self._view_records()

    def _return_book(self):
        values = ask_multi_field(self, "Return book", [
            ("Record ID", "record_id"),
            ("Return date (YYYY-MM-DD)", "return_date"),
        ])
        if values is None:
            return
        message = self.admin.record_return(values["record_id"], values["return_date"])
        messagebox.showinfo("Return book", message)
        self._view_records()

    def _pay_fine(self):
        fine_id = simpledialog.askstring("Pay a fine", "Fine ID:", parent=self)
        if not fine_id:
            return
        message = self.admin.pay_fine(fine_id)
        messagebox.showinfo("Pay a fine", message)
        self._view_fines()
