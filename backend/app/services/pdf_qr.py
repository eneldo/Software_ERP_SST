# ============================================================
# ERP SST ENTERPRISE
# FASE 1.1.8.7.9 — QR PDF PLATINUM
# Archivo: backend/app/services/pdf/pdf_qr.py
# ============================================================

import os
import tempfile
from uuid import uuid4

import qrcode


def generar_qr_temporal(data: str) -> str:
    """Genera QR temporal PNG para insertar en el PDF."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data or "ERP SST ENTERPRISE")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path = os.path.join(tempfile.gettempdir(), f"erp_sst_qr_{uuid4().hex}.png")
    img.save(path)
    return path
