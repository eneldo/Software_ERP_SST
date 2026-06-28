# ============================================================
# SEGURIDAD PASSWORD - ERP SST PRO
# Maneja hash y verificación de contraseñas con bcrypt
# ============================================================

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano a hash seguro.
    """
    return pwd_context.hash(password)


def verify_password(password_plain: str, password_hash: str) -> bool:
    """
    Verifica si la contraseña escrita coincide con el hash guardado.
    """
    return pwd_context.verify(password_plain, password_hash)
