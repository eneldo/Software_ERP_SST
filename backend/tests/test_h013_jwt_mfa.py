# ============================================================
# TESTS: H-013a+b JWT Blocklist + MFA TOTP
# ============================================================

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from app.auth.auth_handler import (
    create_access_token, create_refresh_token,
    decode_access_token, extract_jti,
)
from app.models.token_blocklist import TokenBlocklist


class TestJWTBlocklist:
    def test_access_token_includes_jti(self):
        payload = {
            "user_id": 1,
            "correo": "test@test.com",
            "rol": "ADMIN_EMPRESA",
            "empresa_id": 1,
        }
        token = create_access_token(payload)
        decoded = decode_access_token(token)
        assert "jti" in decoded
        assert decoded["token_type"] == "access"

    def test_refresh_token_includes_jti(self):
        payload = {
            "user_id": 1,
            "correo": "test@test.com",
            "rol": "ADMIN_EMPRESA",
            "empresa_id": 1,
        }
        token = create_refresh_token(payload)
        decoded = decode_access_token(token)
        assert "jti" in decoded
        assert decoded["token_type"] == "refresh"

    def test_extract_jti_returns_jti(self):
        payload = {
            "user_id": 1,
            "correo": "test@test.com",
            "rol": "ADMIN_EMPRESA",
            "empresa_id": 1,
        }
        token = create_access_token(payload)
        jti = extract_jti(token)
        assert jti is not None
        assert len(jti) == 36

    def test_extract_jti_invalid_token(self):
        jti = extract_jti("invalid-token")
        assert jti is None

    def test_token_blocklist_model_fields(self):
        bloqueado = TokenBlocklist(
            jti="test-jti-123",
            token_type="access",
            usuario_id=1,
            empresa_id=1,
            motivo="LOGOUT",
            bloqueado_por=1,
            exp=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        assert bloqueado.jti == "test-jti-123"
        assert bloqueado.token_type == "access"
        assert bloqueado.motivo == "LOGOUT"


class TestTokenBlocklistModel:
    def test_token_blocklist_has_required_fields(self):
        fields = {c.name for c in TokenBlocklist.__table__.columns}
        assert "jti" in fields
        assert "token_type" in fields
        assert "usuario_id" in fields
        assert "empresa_id" in fields
        assert "motivo" in fields
        assert "exp" in fields
        assert "fecha_creacion" in fields


class TestMFATOTP:
    def test_totp_secret_generation(self):
        import pyotp
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert len(code) == 6
        assert totp.verify(code, valid_window=1)

    def test_totp_code_rejects_wrong_code(self):
        import pyotp
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        assert not totp.verify("000000", valid_window=1)

    def test_totp_provisioning_uri(self):
        import pyotp
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name="test@test.com",
            issuer_name="ERP-SST-PRO",
        )
        assert "otpauth://totp/" in uri
        assert "ERP-SST-PRO" in uri
        assert "test%40test.com" in uri
