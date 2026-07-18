import bcrypt

from database import create_user, get_user_by_email


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register(email: str, password: str) -> str:
    existing = get_user_by_email(email)
    if existing:
        return "该邮箱已注册"
    password_hash = hash_password(password)
    create_user(email, password_hash)
    return ""


def login(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    if not check_password(password, user["password_hash"]):
        return None
    return dict(user)
