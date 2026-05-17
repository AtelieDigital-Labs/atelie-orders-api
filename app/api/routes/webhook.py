from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.webhook_service import WebhookService
from typing import Annotated

router = APIRouter(prefix="/api/v1/orders/webhook", tags=["Webhooks"])


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/mercadopago")
async def mercadopago_webhook(request: Request, session: SessionDep):
    """
    Endpoint para receber notificações de pagamento do Mercado Pago.
    """
    try:
        result = await WebhookService.process_mercadopago_webhook(request, session)
        
        return {"received": True, "details": result}
        
    except Exception as e:
        await session.rollback()
        print(f"Erro no Webhook do Mercado Pago: {e}")
        
        return {"received": False, "error": str(e)}