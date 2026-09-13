"""GUI entry point for the Library Management System (Group 02).

Run with:  python -m app.gui_main

This is a Tkinter-based graphical version of the exact same system --
it calls the same auth.py / member_ops.py / admin_ops.py / fines.py
functions as the console app (app/main.py). Neither entry point
affects the other; both read and write the same data/sample_data.json.
"""
from .gui.app import main

if __name__ == "__main__":
    main()
