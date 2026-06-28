from app.database import SessionLocal
from app.services.pdf.inspeccion_pdf_platinum import generar_reporte_inspeccion_platinum_pdf

if __name__ == '__main__':
    db = SessionLocal()
    try:
        pdf = generar_reporte_inspeccion_platinum_pdf(db=db, inspeccion_id=1, usuario='Sistema', base_url=None)
        print('PDF generated, size=', len(pdf))
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()
