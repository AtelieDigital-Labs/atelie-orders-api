from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.webhook_service import WebhookService
from typing import Annotated
from app.api.dependencies.webhook import get_webhook_service, SessionDep

router = APIRouter(prefix="/api/v1/orders/webhook", tags=["Webhooks"])



@router.post("/mercadopago")
async def mercadopago_webhook(
    request: Request, 
    session: AsyncSession = SessionDep,
    service: WebhookService = Depends(get_webhook_service)
):
    """
    Endpoint para receber notificações de pagamento do Mercado Pago.
    """
    try:
        result = await service.process_mercadopago_webhook(
            request=request
        )
        
        return {"received": True, "details": result}
        
    except Exception as e:
        await session.rollback()
        print(f"Erro no Webhook do Mercado Pago: {e}")
        
        return {"received": False, "error": str(e)}