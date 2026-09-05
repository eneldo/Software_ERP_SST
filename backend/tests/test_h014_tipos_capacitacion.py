# ============================================================
# TESTS: H-014 Tipos normativos de capacitación
# ============================================================

import pytest

from app.models.capacitacion import CapacitacionSST
from app.schemas.capacitacion import CapacitacionCreate, CapacitacionResponse


class TestH014TiposCapacitacion:
    def test_model_has_tipo_capacitacion_field(self):
        columns = {c.name for c in CapacitacionSST.__table__.columns}
        assert "tipo_capacitacion" in columns
        assert "riesgo_asociado" in columns

    def test_tipo_capacitacion_default(self):
        cap = CapacitacionSST(
            empresa_id=1,
            nombre="Test",
            tema="Test",
            tipo_capacitacion="CAPACITACION_GENERAL",
        )
        assert cap.tipo_capacitacion == "CAPACITACION_GENERAL"

    def test_tipo_capacitacion_valid_values(self):
        valid_types = [
            "INDUCCION", "REINDUCCION", "RIESGO_ESPECIFICO",
            "CAPACITACION_GENERAL", "CONTINUA",
        ]
        for tipo in valid_types:
            cap = CapacitacionSST(
                empresa_id=1,
                nombre="Test",
                tema="Test",
                tipo_capacitacion=tipo,
            )
            assert cap.tipo_capacitacion == tipo

    def test_riesgo_asociado_optional(self):
        cap = CapacitacionSST(
            empresa_id=1,
            nombre="Test",
            tema="Test",
            tipo_capacitacion="RIESGO_ESPECIFICO",
        )
        assert cap.riesgo_asociado is None

    def test_riesgo_asociado_with_value(self):
        cap = CapacitacionSST(
            empresa_id=1,
            nombre="Test",
            tema="Test",
            tipo_capacitacion="RIESGO_ESPECIFICO",
            riesgo_asociado="Caída de altura",
        )
        assert cap.riesgo_asociado == "Caída de altura"

    def test_schema_create_includes_tipo_capacitacion(self):
        data = CapacitacionCreate(
            empresa_id=1,
            nombre="Inducción SST",
            tema="Inducción",
            tipo_capacitacion="INDUCCION",
        )
        assert data.tipo_capacitacion == "INDUCCION"

    def test_schema_create_default_tipo_capacitacion(self):
        data = CapacitacionCreate(
            empresa_id=1,
            nombre="Capacitación General",
            tema="General",
        )
        assert data.tipo_capacitacion == "CAPACITACION_GENERAL"

    def test_schema_response_includes_tipo_capacitacion(self):
        fields = CapacitacionResponse.model_fields
        assert "tipo_capacitacion" in fields
        assert "riesgo_asociado" in fields
