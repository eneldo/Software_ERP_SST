from sqlalchemy import create_engine

DATABASE_URL = "postgresql://sst_user:Sst_ERP_2026*@localhost:5432/sst_erp"

engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("✅ Conexión exitosa PostgreSQL")
    conn.close()

except Exception as e:
    print("❌ Error:", e)