from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido = Column(String)
    ci = Column(String, unique=True, index=True)
    
    cuentas = relationship("CuentaDebito", back_populates="cliente")
    facturas = relationship("FacturaPendiente", back_populates="cliente")

class CuentaDebito(Base):
    __tablename__ = "cuenta_debito"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    nro_cuenta = Column(String, index=True)
    saldo = Column(Float)
    
    cliente = relationship("Cliente", back_populates="cuentas")
    pagos = relationship("PagoServicio", back_populates="cuenta")

class FacturaPendiente(Base):
    __tablename__ = "factura_pendientes"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    nrofactura = Column(String, index=True)
    saldoPendiente = Column(Float)
    
    cliente = relationship("Cliente", back_populates="facturas")

class PagoServicio(Base):
    __tablename__ = "pagos_servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, default=lambda: datetime.now().isoformat())
    id_cuenta_debito = Column(Integer, ForeignKey("cuenta_debito.id"))
    monto = Column(Float)
    nro_factura = Column(String)
    
    cuenta = relationship("CuentaDebito", back_populates="pagos")