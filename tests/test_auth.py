from app.auth import authenticate_member, authenticate_admin
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
