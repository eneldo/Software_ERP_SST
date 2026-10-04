from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile

from app.routers import auditoria_hallazgo_evidencias as auditoria_upload
from app.routers import biblioteca_documental as biblioteca
from app.routers import firmas_digitales as firmas
from app.schemas.biblioteca_documental_schema import BibliotecaDocumentalCreate


def _upload(nombre: str, contenido: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        filename=nombre,
        file=BytesIO(contenido),
        headers={"content-type": content_type},
    )


def _query(first=None, all_items=None):
    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.first.return_value = first
    query.all.return_value = all_items or []
    return query


def test_auditoria_upload_rechaza_magic_bytes_y_no_escribe_archivo(tmp_path):
    db = MagicMock()
    hallazgo = SimpleNamespace(id=7, auditoria_id=4, empresa_id=2)

    with patch.object(auditoria_upload, "EVIDENCIAS_DIR", tmp_path), patch.object(
        auditoria_upload, "obtener_hallazgo_o_404", return_value=hallazgo
    ):
        with pytest.raises(HTTPException) as error:
            auditoria_upload.subir_evidencia_hallazgo(
                hallazgo_id=7,
                descripcion="",
                tipo="FOTO",
                file=_upload("evidencia.pdf", b"contenido falso", "application/pdf"),
                db=db,
                usuario=SimpleNamespace(id=3),
            )

    assert error.value.status_code == 400
    assert list(tmp_path.iterdir()) == []
    db.add.assert_not_called()


def test_auditoria_upload_elimina_archivo_si_falla_commit(tmp_path):
    db = MagicMock()
    db.commit.side_effect = RuntimeError("db error")
    hallazgo = SimpleNamespace(id=7, auditoria_id=4, empresa_id=2)

    with patch.object(auditoria_upload, "EVIDENCIAS_DIR", tmp_path), patch.object(
        auditoria_upload, "obtener_hallazgo_o_404", return_value=hallazgo
    ):
        with pytest.raises(RuntimeError):
            auditoria_upload.subir_evidencia_hallazgo(
                hallazgo_id=7,
                descripcion="",
                tipo="FOTO",
                file=_upload("evidencia.pdf", b"%PDF-1.7\n%%EOF", "application/pdf"),
                db=db,
                usuario=SimpleNamespace(id=3),
            )

    assert list(tmp_path.iterdir()) == []
    db.rollback.assert_called_once()


def test_biblioteca_create_rechaza_archivo_inactivo_o_de_otro_tenant():
    db = MagicMock()
    db.query.side_effect = [
        _query(SimpleNamespace(id=1)),
        _query(None),
    ]
    data = BibliotecaDocumentalCreate(
        empresa_id=1,
        archivo_id=9,
        codigo_documental="DOC-1",
        titulo="Documento",
        categoria="POLITICA",
        tipo_documento="PDF",
    )

    with pytest.raises(HTTPException) as error:
        biblioteca.crear_documento_biblioteca(
            data=data,
            db=db,
            usuario=SimpleNamespace(id=2, empresa_id=1, rol="ADMIN_EMPRESA"),
        )

    assert error.value.status_code == 404
    db.add.assert_not_called()


def test_biblioteca_upload_es_atomico_y_compensa_archivo(tmp_path):
    db = MagicMock()
    db.query.return_value = _query(SimpleNamespace(id=1))
    db.flush.side_effect = [None, RuntimeError("documento invalido")]

    with patch.object(biblioteca, "BASE_UPLOAD_DIR", tmp_path):
        with pytest.raises(RuntimeError):
            biblioteca.subir_documento_biblioteca(
                empresa_id=1,
                codigo_documental="DOC-1",
                titulo="Documento",
                categoria="POLITICA",
                tipo_documento="PDF",
                modulo_origen=None,
                version="1.0",
                estado="BORRADOR",
                responsable=None,
                descripcion=None,
                palabras_clave=None,
                fecha_aprobacion=None,
                fecha_vencimiento=None,
                file=_upload("documento.pdf", b"%PDF-1.7\n%%EOF", "application/pdf"),
                db=db,
                usuario=SimpleNamespace(id=2, empresa_id=1, rol="ADMIN_EMPRESA"),
            )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
    assert list(tmp_path.iterdir()) == []


def test_firmas_rechaza_usuario_objetivo_de_otro_tenant():
    db = MagicMock()
    db.query.return_value = _query(SimpleNamespace(id=8, empresa_id=2))

    with pytest.raises(HTTPException) as error:
        firmas.listar_firmas_usuario(
            usuario_id=8,
            db=db,
            usuario_actual=SimpleNamespace(id=3, empresa_id=1, rol="ADMIN_EMPRESA"),
        )

    assert error.value.status_code == 403


def test_firmas_rechaza_operacion_por_id_de_otro_tenant():
    db = MagicMock()
    firma = SimpleNamespace(id=5, usuario_id=8, activo=True)
    propietario = SimpleNamespace(id=8, empresa_id=2)
    db.query.side_effect = [_query(firma), _query(propietario)]

    with pytest.raises(HTTPException) as error:
        firmas.activar_firma(
            firma_id=5,
            db=db,
            usuario_actual=SimpleNamespace(id=3, empresa_id=1, rol="ADMIN_EMPRESA"),
        )

    assert error.value.status_code == 403
    db.commit.assert_not_called()
