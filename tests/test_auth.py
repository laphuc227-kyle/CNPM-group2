import pytest

from app.auth import authenticate_member, authenticate_admin, register_member
from app.models import Member, Administrator


def test_member_login_success():
    member = authenticate_member("member01", "123456")
    assert member is not None
    assert isinstance(member, Member)
    assert member.member_id == "LIB001"


def test_member_login_fail():
    assert authenticate_member("wrong", "wrong") is None


def test_admin_login_success():
    admin = authenticate_admin("admin", "admin123")
    assert admin is not None
    assert isinstance(admin, Administrator)


def test_admin_login_fail():
    assert authenticate_admin("wrong", "wrong") is None


def test_register_creates_a_working_login():
    member = register_member(
        username="newuser01", password="pass123", full_name="New User",
        email="newuser01@ut.edu.vn", date_of_birth="2002-03-04",
        address="1 Test St", membership_type="Standard",
    )
    assert isinstance(member, Member)
    assert member.username == "newuser01"

    logged_in = authenticate_member("newuser01", "pass123")
    assert logged_in is not None
    assert logged_in.member_id == member.member_id


def test_register_rejects_duplicate_username():
    with pytest.raises(ValueError):
        register_member(
            username="member01", password="whatever", full_name="Someone Else",
            email="someone@ut.edu.vn", date_of_birth="2000-01-01",
            address="2 Test St", membership_type="Standard",
        )
