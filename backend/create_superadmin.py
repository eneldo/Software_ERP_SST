"""Script para crear un usuario Super Administrador.

Uso:
    python create_superadmin.py

Las credenciales se leen de variables de entorno o se generan aleatoriamente.
Nunca usar credenciales hardcodeadas en producción.
"""

import os
import secrets
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bcrypt
from app.database import SessionLocal
from app.models.usuario import Usuario


def _generate_password(length: int = 20) -> str:
    """Genera una contraseña aleatoria segura."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            return password


def hash_password_direct(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def crear_superadmin():
    correo = os.environ.get("SUPER_ADMIN_EMAIL", "admin@sistema-sst.com")
    password = os.environ.get("SUPER_ADMIN_PASSWORD")
    generated = False

    if not password:
        password = _generate_password()
        generated = True

    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.correo == correo.lower()).first()
        if existe:
            print(f"Ya existe un usuario con el correo: {correo}")
            print(f"  ID: {existe.id} | Rol: {existe.rol} | Activo: {existe.activo}")
            return

        usuario = Usuario(
            nombres="Super",
            apellidos="Administrador",
            correo=correo.lower(),
            password=hash_password_direct(password),
            rol="SUPER_ADMIN",
            activo=True,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        print("Usuario Super Administrador creado exitosamente:")
        print(f"  ID:       {usuario.id}")
        print(f"  Nombre:   {usuario.nombres} {usuario.apellidos}")
        print(f"  Correo:   {usuario.correo}")
        print(f"  Rol:      {usuario.rol}")
        print(f"  Activo:   {usuario.activo}")

        if generated:
            print(f"\n  Contrasena generada: {password}")
            print("  GUARDE ESTA CONTRASENA EN UN LUGAR SEGURO.")
        else:
            print("\n  Contrasena configurada desde variable de entorno.")
    except Exception as e:
        db.rollback()
        print(f"Error al crear usuario: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    crear_superadmin()
