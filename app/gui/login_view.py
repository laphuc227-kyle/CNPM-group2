import tkinter as tk
from tkinter import ttk

from ..auth import authenticate_member, authenticate_admin


class LoginView(ttk.Frame):
    """Role selector (Member/Admin) + username/password, matching the
    console app's 'Login as (member/admin/exit):' step exactly -- just
    with buttons and text fields instead of typed input()."""

    def __init__(self, parent, on_login, on_register=None):
        super().__init__(parent, padding=40)
        self.on_login = on_login
        self.on_register = on_register
        self.role = tk.StringVar(value="member")

        center = ttk.Frame(self)
        center.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            center, text="Library Management System", style="Heading.TLabel"
        ).pack(pady=(0, 2))
        ttk.Label(center, text="Group 02", foreground="#666666").pack(pady=(0, 20))

        role_frame = ttk.Frame(center)
        role_frame.pack(pady=(0, 16))
        ttk.Radiobutton(
            role_frame, text="Member", variable=self.role, value="member"
        ).pack(side="left", padx=6)
        ttk.Radiobutton(
            role_frame, text="Admin", variable=self.role, value="admin"
        ).pack(side="left", padx=6)

        form = ttk.Frame(center)
        form.pack(fill="x")

        ttk.Label(form, text="Username").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.username_entry = ttk.Entry(form, width=28)
        self.username_entry.grid(row=1, column=0, pady=(0, 12))

        ttk.Label(form, text="Password").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.password_entry = ttk.Entry(form, width=28, show="*")
        self.password_entry.grid(row=3, column=0, pady=(0, 12))

        self.error_label = ttk.Label(center, text="", style="Error.TLabel")
        self.error_label.pack(pady=(0, 8))

        login_btn = ttk.Button(
            center, text="Log in", style="Accent.TButton", command=self._attempt_login
        )
        login_btn.pack(fill="x")

        if self.on_register is not None:
            ttk.Button(
                center, text="New here? Create a member account",
                command=self.on_register,
            ).pack(fill="x", pady=(8, 0))

        # Enter key submits from either field
        self.username_entry.bind("<Return>", lambda e: self._attempt_login())
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())
        self.username_entry.focus_set()

    def _attempt_login(self):
        role = self.role.get()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.config(text="Enter both username and password.")
            return

        if role == "member":
            user = authenticate_member(username, password)
        else:
            user = authenticate_admin(username, password)

        if user is None:
            self.error_label.config(text="Login failed.")
            self.password_entry.delete(0, tk.END)
            return

        self.error_label.config(text="")
        self.on_login(role, user)
