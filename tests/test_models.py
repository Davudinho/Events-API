from models import User


def test_user_password_hashing_behaves_correctly():
    user = User(username="test_user")

    user.set_password("MyPassword123!")

    assert user.password_hash is not None
    assert user.password_hash != "MyPassword123!"
    assert user.check_password("MyPassword123!") is True
    assert user.check_password("WrongPassword123!") is False