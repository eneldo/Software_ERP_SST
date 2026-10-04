from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from app.database import Base


class CapacitacionAsistente(Base):
    __tablename__ = "capacitacion_asistentes"

    id = Column(Integer, primary_key=True)

    capacitacion_id = Column(Integer, ForeignKey("capacitaciones_sst.id"))

    nombre = Column(String(250))
    documento = Column(String(50))
    cargo = Column(String(150))

    asistio = Column(Boolean, default=False)

    observaciones = Column(Text)

    activo = Column(Boolean, default=True)
