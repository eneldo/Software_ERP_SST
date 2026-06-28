from contextlib import closing

from app.database import SessionLocal
from app.services.pdf.inspeccion_pdf_platinum import generar_reporte_inspeccion_platinum_pdf


def main() -> None:
    with closing(SessionLocal()) as db:
        pdf = generar_reporte_inspeccion_platinum_pdf(
            db=db,
            inspeccion_id=1,
            usuario='Sistema',
            base_url=None,
        )
        print('PDF generated, size=', len(pdf))


if __name__ == '__main__':
    main()
