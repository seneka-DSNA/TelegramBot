# passwords.py
import bcrypt


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    """
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

