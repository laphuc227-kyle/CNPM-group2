import tkinter as tk
from tkinter import ttk


def ask_multi_field(parent, title, fields):
    """Opens a modal dialog with one Entry per (label, key) in `fields`.
    Returns a dict {key: value} on OK, or None if cancelled/closed.
    `fields` is a list of (label_text, key) or (label_text, key, default)."""
    result = {}

    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent.winfo_toplevel())
    dialog.resizable(False, False)
    dialog.grab_set()

    form = ttk.Frame(dialog, padding=16)
    form.pack(fill="both", expand=True)

    entries = {}
    for i, field in enumerate(fields):
        label_text, key = field[0], field[1]
        default = field[2] if len(field) > 2 else ""
        ttk.Label(form, text=label_text).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 8))
        entry = ttk.Entry(form, width=32)
        entry.insert(0, default)
        entry.grid(row=i, column=1, pady=4)
        entries[key] = entry

    if fields:
        entries[fields[0][1]].focus_set()

    button_row = ttk.Frame(form)
    button_row.grid(row=len(fields), column=0, columnspan=2, pady=(12, 0), sticky="e")

    def on_ok():
        for label_text, key, *_ in fields:
            result[key] = entries[key].get().strip()
        dialog.destroy()

    def on_cancel():
        result.clear()
        result["__cancelled__"] = True
        dialog.destroy()

    ttk.Button(button_row, text="Cancel", command=on_cancel).pack(side="right", padx=(8, 0))
    ttk.Button(button_row, text="OK", style="Accent.TButton", command=on_ok).pack(side="right")

    dialog.bind("<Return>", lambda e: on_ok())
    dialog.bind("<Escape>", lambda e: on_cancel())
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    dialog.update_idletasks()
    x = parent.winfo_toplevel().winfo_x() + 60
    y = parent.winfo_toplevel().winfo_y() + 60
    dialog.geometry(f"+{x}+{y}")

    parent.wait_window(dialog)

    if result.get("__cancelled__"):
        return None
    return result
