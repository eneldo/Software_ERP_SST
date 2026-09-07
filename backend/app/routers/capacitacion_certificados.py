# ============================================================
# ROUTER: CERTIFICADOS DE CAPACITACIÓN SST
# FASE 2.7.4 - HARDENING ENTERPRISE CAPACITACIONES SST
# ============================================================

from pathlib import Path
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.capacitacion import CapacitacionSST, CapacitacionAsistenteSST
from app.models.capacitacion_certificado import CapacitacionCertificado
from app.schemas.capacitacion_certificado import CapacitacionCertificadoResponse

router = APIRouter(
    prefix="/hacer/capacitaciones",
    tags=["HACER - Certificados Capacitaciones SST"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST", "AUDITOR"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"]

CERTIFICADOS_DIR = Path(__file__).resolve().parent.parent / "uploads" / "certificados"
CERTIFICADOS_DIR.mkdir(parents=True, exist_ok=True)


def generar_pdf_certificado(capacitacion: CapacitacionSST, asistente: CapacitacionAsistenteSST, ruta_pdf: Path):
    c = canvas.Canvas(str(ruta_pdf), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 90, "CERTIFICADO DE CAPACITACIÓN SST")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 130, "Se certifica que:")

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 165, asistente.nombres or "")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 190, f"Documento: {asistente.documento or 'No registrado'}")

    c.drawCentredString(width / 2, height - 230, "Participó en la capacitación:")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 260, capacitacion.nombre or "")

    c.setFont("Helvetica", 11)
    c.drawString(90, height - 310, f"Tema: {capacitacion.tema or ''}")
    c.drawString(90, height - 335, f"Modalidad: {capacitacion.modalidad or ''}")
    c.drawString(90, height - 360, f"Fecha: {capacitacion.fecha_ejecucion or capacitacion.fecha_programada or ''}")
    c.drawString(90, height - 385, f"Duración: {capacitacion.duracion_horas or 0} horas")
    c.drawString(90, height - 410, f"Capacitador: {capacitacion.capacitador or ''}")

    try:
        import qrcode
        qr_data = f"ERP-SST|CERT|CAP-{capacitacion.id}|ASIST-{asistente.id}|DOC-{asistente.documento}|FECHA-{capacitacion.fecha_ejecucion or capacitacion.fecha_programada}"
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        qr_img = ImageReader(qr_buffer)
        c.drawImage(qr_img, width - 150, 60, width=80, height=80)
        c.setFont("Helvetica", 7)
        c.drawCentredString(width - 110, 50, "Verificación QR")
    except ImportError:
        pass

    c.line(90, 150, 260, 150)
    c.drawString(110, 130, "Responsable SST")

    c.line(350, 150, 520, 150)
    c.drawString(395, 130, "Capacitador")

    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 70, "Documento generado por ERP SST PRO")
    c.save()


@router.post("/{capacitacion_id}/certificados/{asistente_id}", response_model=CapacitacionCertificadoResponse)
def generar_certificado(
    capacitacion_id: int,
    asistente_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    capacitacion = db.query(CapacitacionSST).filter(CapacitacionSST.id == capacitacion_id).first()
    if not capacitacion:
        raise HTTPException(status_code=404, detail="Capacitación no encontrada")

    asistente = (
        db.query(CapacitacionAsistenteSST)
        .filter(
            CapacitacionAsistenteSST.id == asistente_id,
            CapacitacionAsistenteSST.capacitacion_id == capacitacion_id,
            CapacitacionAsistenteSST.activo == True,
        )
        .first()
    )
    if not asistente:
        raise HTTPException(status_code=404, detail="Asistente no encontrado")

    if not asistente.asistio:
        raise HTTPException(status_code=400, detail="No se puede generar certificado a un asistente marcado como no asistió")

    nombre_pdf = f"cert_cap_{capacitacion_id}_{asistente_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_pdf = CERTIFICADOS_DIR / nombre_pdf
    generar_pdf_certificado(capacitacion, asistente, ruta_pdf)

    certificado = CapacitacionCertificado(
        capacitacion_id=capacitacion_id,
        asistente_id=asistente_id,
        archivo_pdf=f"/uploads/certificados/{nombre_pdf}",
        fecha_generacion=datetime.now(),
        activo=True,
    )

    db.add(certificado)
    asistente.certificado_generado = True
    db.commit()
    db.refresh(certificado)
    return certificado


@router.get("/{capacitacion_id}/certificados", response_model=list[CapacitacionCertificadoResponse])
def listar_certificados(
    capacitacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return (
        db.query(CapacitacionCertificado)
        .filter(
            CapacitacionCertificado.capacitacion_id == capacitacion_id,
            CapacitacionCertificado.activo == True,
        )
        .order_by(CapacitacionCertificado.id.desc())
        .all()
    )


@router.get("/certificados/{certificado_id}/descargar")
def descargar_certificado(
    certificado_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    certificado = db.query(CapacitacionCertificado).filter(CapacitacionCertificado.id == certificado_id).first()

    if not certificado or not certificado.archivo_pdf:
        raise HTTPException(status_code=404, detail="Certificado no encontrado")

    ruta_relativa = certificado.archivo_pdf.replace("/uploads/", "")
    ruta_fisica = Path(__file__).resolve().parent.parent / "uploads" / ruta_relativa

    if not ruta_fisica.exists():
        raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")

    return FileResponse(path=str(ruta_fisica), media_type="application/pdf", filename=ruta_fisica.name)


@router.get("/certificados/verificar/{certificado_id}")
def verificar_certificado(
    certificado_id: int,
    db: Session = Depends(get_db),
):
    certificado = db.query(CapacitacionCertificado).filter(CapacitacionCertificado.id == certificado_id).first()

    if not certificado:
        return {"valido": False, "mensaje": "Certificado no encontrado"}

    capacitacion = db.query(CapacitacionSST).filter(CapacitacionSST.id == certificado.capacitacion_id).first()
    asistente = (
        db.query(CapacitacionAsistenteSST)
        .filter(CapacitacionAsistenteSST.id == certificado.asistente_id)
        .first()
    )

    return {
        "valido": True,
        "certificado_id": certificado.id,
        "capacitacion": capacitacion.nombre if capacitacion else None,
        "fecha_capacitacion": str(capacitacion.fecha_ejecucion or capacitacion.fecha_programada) if capacitacion else None,
        "asistente": asistente.nombres if asistente else None,
        "documento": asistente.documento if asistente else None,
        "fecha_generacion": str(certificado.fecha_generacion),
        "empresa_id": capacitacion.empresa_id if capacitacion else None,
    }
