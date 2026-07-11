import os
import sys

from sqlalchemy import create_engine


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: Debe definir la variable de entorno DATABASE_URL.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("Conexion exitosa PostgreSQL")
    conn.close()

except Exception as exc:
    print("Error conectando a PostgreSQL:", exc)
    sys.exit(1)
