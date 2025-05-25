from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from database.models import Cliente, FacturaPendiente
from pydantic import BaseModel

router = APIRouter(prefix="/api/telco", tags=["telco"])

class FacturaResponse(BaseModel):
    nrofactura: str
    saldoPendiente: float

@router.get("/consultar_deuda/{ci}", response_model=List[FacturaResponse])
async def consultar_deuda(ci: str, db: Session = Depends(get_db)):
    """
    Consulta las facturas pendientes de un cliente por su CI
    """
    # Buscar el cliente por CI
    cliente = db.query(Cliente).filter(Cliente.ci == ci).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CI {ci} no encontrado"
        )
    
    # Obtener las facturas pendientes del cliente
    facturas = db.query(FacturaPendiente).filter(FacturaPendiente.cliente_id == cliente.id).all()
    
    # Formatear la respuesta
    return [
        FacturaResponse(
            nrofactura=factura.nrofactura,
            saldoPendiente=factura.saldoPendiente
        ) for factura in facturas
    ]

class PagoRequest(BaseModel):
    nro_factura: str
    monto: float

class PagoResponse(BaseModel):
    success: bool
    message: str
    saldo_restante: float = None

@router.post("/pagar_deuda", response_model=PagoResponse)
async def pagar_deuda(pago: PagoRequest, db: Session = Depends(get_db)):
    """
    Registra el pago de una factura
    """
    # Buscar la factura
    factura = db.query(FacturaPendiente).filter(FacturaPendiente.nrofactura == pago.nro_factura).first()
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {pago.nro_factura} no encontrada"
        )
    
    # Validar que el monto no supere el saldo pendiente
    if pago.monto > factura.saldoPendiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El monto ({pago.monto}) supera el saldo pendiente de la factura ({factura.saldoPendiente})"
        )
    
    # Actualizar el saldo pendiente
    factura.saldoPendiente -= pago.monto
    db.commit()
    
    return PagoResponse(
        success=True,
        message=f"Pago de {pago.monto} registrado correctamente para la factura {pago.nro_factura}",
        saldo_restante=factura.saldoPendiente
    )