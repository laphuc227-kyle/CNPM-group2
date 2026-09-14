import tkinter as tk
from tkinter import ttk

from .login_view import LoginView
from .register_view import RegisterView
from .member_view import MemberView
from .admin_view import AdminView


class App(tk.Tk):
    """Root window for the GUI version of the Library Management System.

    This is a thin visual layer only -- every action calls straight into
    the exact same business-logic functions used by the console app
    (app/auth.py, app/member_ops.py, app/admin_ops.py, app/fines.py).
    Nothing in those files is modified; the console app (app/main.py)
    keeps working exactly as before, unaffected by this GUI.
    """

    def __init__(self):
        super().__init__()
        self.title("Library Management System (Group 02)")
        self.geometry("900x600")
        self.minsize(760, 520)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Sidebar.TFrame", background="#f2f2f2")
        style.configure(
            "SidebarItem.TButton", anchor="w", padding=(10, 8), relief="flat",
            font=("TkDefaultFont", 10)
        )
        style.configure("Accent.TButton", padding=(10, 6))
        style.configure("Heading.TLabel", font=("TkDefaultFont", 14, "bold"))
        style.configure("Error.TLabel", foreground="#b3261e")

        self._container = ttk.Frame(self)
        self._container.pack(fill="both", expand=True)

        self.show_login()

    # ---------- View switching ----------

    def _clear(self):
        for widget in self._container.winfo_children():
            widget.destroy()

    def show_login(self):
        self._clear()
        LoginView(
            self._container, on_login=self._handle_login, on_register=self.show_register
        ).pack(fill="both", expand=True)

    def show_register(self):
        self._clear()
        RegisterView(
            self._container, on_registered=self._handle_registered, on_cancel=self.show_login
        ).pack(fill="both", expand=True)

    def _handle_registered(self, member):
        # New account created -- log the person straight in as a member.
        self.show_member(member)

    def _handle_login(self, role, user):
        if role == "member":
            self.show_member(user)
        else:
            self.show_admin(user)

    def show_member(self, member):
        self._clear()
        MemberView(self._container, member=member, on_logout=self.show_login).pack(
            fill="both", expand=True
        )

    def show_admin(self, admin):
        self._clear()
        AdminView(self._container, admin=admin, on_logout=self.show_login).pack(
            fill="both", expand=True
        )


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
