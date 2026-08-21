"""Genera secretos seguros para produccion.

Uso:
    python scripts/generate_secrets.py

Genera SECRET_KEY y POSTGRES_PASSWORD con entropia criptografica.
"""
import secrets
import string


def generate_secret_key(length: int = 64) -> str:
    """Genera una clave secreta de longitud especificada."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_password(length: int = 24) -> str:
    """Genera un password seguro con caracteres especiales."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


if __name__ == "__main__":
    print("=" * 50)
    print("  ERP SST PRO - Generador de Secretos")
    print("=" * 50)
    print()
    print(f"SECRET_KEY={generate_secret_key(64)}")
    print(f"POSTGRES_PASSWORD={generate_password(24)}")
    print()
    print("Copia estos valores en tus archivos .env")
    print("=" * 50)
