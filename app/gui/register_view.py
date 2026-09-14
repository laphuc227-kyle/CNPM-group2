import tkinter as tk
from tkinter import ttk

from ..auth import register_member


class RegisterView(ttk.Frame):
    """Self-registration form for a new Member account -- the GUI
    counterpart of the console app's 'register' option at login.
    On success, hands the newly created Member back to on_registered
    so the caller can log the person straight in (or send them back
    to the login screen); calls on_cancel to go back without creating
    an account."""

    def __init__(self, parent, on_registered, on_cancel):
        super().__init__(parent, padding=40)
        self.on_registered = on_registered
        self.on_cancel = on_cancel

        center = ttk.Frame(self)
        center.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            center, text="Create Member Account", style="Heading.TLabel"
        ).pack(pady=(0, 20))

        form = ttk.Frame(center)
        form.pack(fill="x")

        self.fields = {}
        field_defs = [
            ("username", "Username"),
            ("password", "Password"),
            ("full_name", "Full Name"),
            ("email", "Email"),
            ("date_of_birth", "Date of Birth (YYYY-MM-DD)"),
            ("address", "Address"),
        ]
        for row, (key, label) in enumerate(field_defs):
            ttk.Label(form, text=label).grid(row=row * 2, column=0, sticky="w", pady=(0, 2))
            show = "*" if key == "password" else ""
            entry = ttk.Entry(form, width=34, show=show)
            entry.grid(row=row * 2 + 1, column=0, pady=(0, 10))
            self.fields[key] = entry

        ttk.Label(form, text="Membership Type").grid(
            row=len(field_defs) * 2, column=0, sticky="w", pady=(0, 2)
        )
        self.membership_type = tk.StringVar(value="Standard")
        ttk.Combobox(
            form, textvariable=self.membership_type,
            values=["Standard", "Premium"], state="readonly", width=31,
        ).grid(row=len(field_defs) * 2 + 1, column=0, pady=(0, 10))

        self.error_label = ttk.Label(center, text="", style="Error.TLabel")
        self.error_label.pack(pady=(4, 8))

        btn_row = ttk.Frame(center)
        btn_row.pack(fill="x")
        ttk.Button(
            btn_row, text="Create Account", style="Accent.TButton",
            command=self._submit,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(
            btn_row, text="Back to Login", command=self.on_cancel,
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.fields["username"].focus_set()

    def _submit(self):
        values = {key: entry.get().strip() for key, entry in self.fields.items()}
        if not all(values.values()):
            self.error_label.config(text="Please fill in every field.")
            return

        try:
            member = register_member(
                username=values["username"], password=values["password"],
                full_name=values["full_name"], email=values["email"],
                date_of_birth=values["date_of_birth"], address=values["address"],
                membership_type=self.membership_type.get(),
            )
        except ValueError as e:
            self.error_label.config(text=str(e))
            return

        self.on_registered(member)
