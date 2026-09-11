# ============================================================
# SEGURIDAD PASSWORD - ERP SST PRO
# Maneja hash y verificación de contraseñas con bcrypt
# ============================================================

import bcrypt


def hash_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano a hash seguro.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password_plain: str, password_hash: str) -> bool:
    """
    Verifica si la contraseña escrita coincide con el hash guardado.
    """
    try:
        return bcrypt.checkpw(
            password_plain.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except Exception:
        return False
