"""Script para crear un usuario Super Administrador."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bcrypt
from app.database import SessionLocal
from app.models.usuario import Usuario


CORREO = "admin@sistema-sst.com"
PASSWORD = "SuperAdmin2026*"
NOMBRES = "Super"
APELLIDOS = "Administrador"
ROL = "SUPER_ADMIN"


def hash_password_direct(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def crear_superadmin():
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.correo == CORREO.lower()).first()
        if existe:
            print(f"Ya existe un usuario con el correo: {CORREO}")
            print(f"  ID: {existe.id} | Rol: {existe.rol} | Activo: {existe.activo}")
            return

        usuario = Usuario(
            nombres=NOMBRES,
            apellidos=APELLIDOS,
            correo=CORREO.lower(),
            password=hash_password_direct(PASSWORD),
            rol=ROL,
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
        print(f"\n  Contrasena: {PASSWORD}")
    except Exception as e:
        db.rollback()
        print(f"Error al crear usuario: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    crear_superadmin()
