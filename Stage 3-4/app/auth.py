"""Authentication -- looks up credentials and returns the matching
domain object (Member or Administrator) from models.py, or None if
the login fails. Part of the Business Layer."""
from .db import load_data
from .models import Member, Administrator


def authenticate_member(username, password):
    data = load_data()
    for m in data["members"]:
        if m["username"] == username and m["password"] == password:
            return Member.from_dict(m)
    return None


def authenticate_admin(username, password):
    admin = Administrator()  # default admin/admin123 credentials
    if admin.login(username, password):
        return admin
    return None
