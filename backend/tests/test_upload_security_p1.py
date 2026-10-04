from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.core.file_security import validate_upload


def upload(nombre: str, contenido: bytes, content_type: str) -> UploadFile:
    return UploadFile(filename=nombre, file=BytesIO(contenido), headers={"content-type": content_type})


def test_validador_rechaza_contenido_disfrazado_de_pdf():
    with pytest.raises(HTTPException) as error:
        validate_upload(upload("examen.pdf", b"contenido ejecutable", "application/pdf"), allowed_extensions={".pdf"})
    assert error.value.status_code == 400


def test_validador_aplica_limite_durante_lectura():
    with pytest.raises(HTTPException) as error:
        validate_upload(upload("perfil.xlsx", b"PK\x03\x04" + b"x" * (1024 * 1024), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), allowed_extensions={".xlsx"}, max_size_mb=1)
    assert error.value.status_code == 413


def test_validador_acepta_pdf_real_dentro_del_limite():
    result = validate_upload(upload("documento.pdf", b"%PDF-1.7\n%%EOF", "application/pdf"), allowed_extensions={".pdf"}, max_size_mb=1)
    assert result.extension == ".pdf"
    assert result.mime_type == "application/pdf"
