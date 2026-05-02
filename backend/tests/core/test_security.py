from app.core.security import hash_password, verify_password

def test_verify_password():
    password = "Pass123"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password) is True