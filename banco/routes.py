from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
from datetime import datetime
from database.database import get_db
from database.models import Cliente, CuentaDebito, PagoServicio, FacturaPendiente
from pydantic import BaseModel

router = APIRouter(prefix="/api/banco", tags=["banco"])

# URL del servicio de Telco
TELCO_API = "http://localhost:8001/api/telco"

class FacturaResponse(BaseModel):
    nrofactura: str
    saldoPendiente: float

@router.get("/consultar_deuda/{ci}", response_model=List[FacturaResponse])
async def consultar_deuda(ci: str, db: Session = Depends(get_db)):
    # Busca el cliente en la base de datos 
    cliente = db.query(Cliente).filter(Cliente.ci == ci).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CI {ci} no encontrado en el banco"
        )
    # Cerramos la sesión antes de la llamada externa
    db.close()

    # Consultar las facturas pendientes en la API de Telco
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{TELCO_API}/consultar_deuda/{ci}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error al consultar la API de Telco: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión con la API de Telco: {str(e)}"
            )

class PagoRequest(BaseModel):
    nro_factura: str
    monto: float
    nro_cuenta: str

class PagoResponse(BaseModel):
    success: bool
    message: str
    fecha: str = None
    saldo_restante: float = None

@router.post("/pagar_deuda", response_model=PagoResponse)
async def pagar_deuda(pago: PagoRequest, db: Session = Depends(get_db)):
    """
    Realiza el pago de una factura
    """
    # Buscar la cuenta de débito
    cuenta = db.query(CuentaDebito).filter(CuentaDebito.nro_cuenta == pago.nro_cuenta).first()
    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuenta {pago.nro_cuenta} no encontrada"
        )
    
    # Verificar que el saldo sea suficiente
    if cuenta.saldo < pago.monto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Saldo actual: {cuenta.saldo}, Monto a pagar: {pago.monto}"
        )
    
    # Verificar que la factura exista y el monto no supere el saldo pendiente
    factura = db.query(FacturaPendiente).filter(FacturaPendiente.nrofactura == pago.nro_factura).first()
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {pago.nro_factura} no encontrada"
        )
    
    if pago.monto > factura.saldoPendiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El monto ({pago.monto}) supera el saldo pendiente de la factura ({factura.saldoPendiente})"
        )
    
    # Cerramos la sesión antes de la llamada externa
    db.close()

    # Realizar el pago en la API de Telco
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TELCO_API}/pagar_deuda",
                json={"nro_factura": pago.nro_factura, "monto": pago.monto}
            )
            response.raise_for_status()
            data = response.json()
            return PagoResponse(**data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error al consultar la API de Telco: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión con la API de Telco: {str(e)}"
            )