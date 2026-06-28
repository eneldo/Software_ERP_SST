# ============================================================
# QR SERVICE PDF PLATINUM - ERP SST PRO
# Archivo: backend/app/services/pdf/pdf_qr.py
# ============================================================

import os
import tempfile
import qrcode


def generar_qr_temporal(data: str) -> str:
    """
    Genera un QR temporal para insertarlo en el PDF.
    Retorna la ruta absoluta del PNG.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )

    qr.add_data(data or "ERP SST PRO")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, "qr_reporte_platinum.png")
    img.save(path)

    return path