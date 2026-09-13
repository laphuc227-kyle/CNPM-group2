import tkinter as tk
from tkinter import ttk

from ..models import Member


class MemberView(ttk.Frame):
    """Member dashboard: a sidebar of the same 5 options as the console's
    MEMBER MENU (plus Logout), and a content area that displays the
    exact text each underlying Member method already returns -- no new
    business logic, just a nicer place to show it."""

    MENU_ITEMS = [
        ("Personal information", "personal_info"),
        ("Search books", "search_books"),
        ("Currently borrowed books", "borrowed_books"),
        ("Borrow history", "borrow_history"),
        ("Fines", "fines"),
    ]

    def __init__(self, parent, member: Member, on_logout):
        super().__init__(parent)
        self.member = member
        self.on_logout = on_logout

        # ---------- Sidebar ----------
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=232)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ttk.Label(
            sidebar, text="MEMBER MENU", background="#f2f2f2",
            foreground="#888888", padding=(12, 12, 12, 4)
        ).pack(fill="x")

        for label, key in self.MENU_ITEMS:
            ttk.Button(
                sidebar, text=label, style="SidebarItem.TButton",
                command=lambda k=key: self._show(k)
            ).pack(fill="x")

        ttk.Frame(sidebar).pack(fill="y", expand=True)  # spacer
        ttk.Button(
            sidebar, text="Logout", style="SidebarItem.TButton",
            command=self.on_logout
        ).pack(fill="x", side="bottom", pady=(0, 8))

        # ---------- Content area ----------
        content = ttk.Frame(self, padding=16)
        content.pack(side="left", fill="both", expand=True)

        self.title_label = ttk.Label(content, text="", style="Heading.TLabel")
        self.title_label.pack(anchor="w", pady=(0, 10))

        self.search_bar = ttk.Frame(content)
        self.search_entry = ttk.Entry(self.search_bar, width=30)
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._run_search())
        ttk.Button(
            self.search_bar, text="Search", command=self._run_search
        ).pack(side="left")

        text_frame = ttk.Frame(content)
        text_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.text_frame = text_frame
        self.output = tk.Text(
            text_frame, wrap="word", state="disabled",
            relief="flat", background="#fafafa", padx=12, pady=12
        )
        scrollbar = ttk.Scrollbar(text_frame, command=self.output.yview)
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._show("personal_info")

    def _write(self, text):
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text)
        self.output.config(state="disabled")

    def _show(self, key):
        self.search_bar.pack_forget()

        if key == "personal_info":
            self.title_label.config(text="Personal information")
            self._write(self.member.view_personal_info())

        elif key == "search_books":
            self.title_label.config(text="Search books")
            self.search_bar.pack(anchor="w", pady=(0, 8), before=self.text_frame)
            self._write("Enter a keyword (title / author / category) and press Search.")

        elif key == "borrowed_books":
            self.title_label.config(text="Currently borrowed books")
            self._write(self.member.view_borrowed_books())

        elif key == "borrow_history":
            self.title_label.config(text="Borrow history")
            self._write(self.member.view_borrow_history())

        elif key == "fines":
            self.title_label.config(text="Fines")
            self._write(self.member.view_fines())

    def _run_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self._write("Enter a keyword first.")
            return
        self._write(Member.search_books(keyword))
