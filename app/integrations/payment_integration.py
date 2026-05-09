from httpx import AsyncClient, HTTPError
import uuid
from app.core.config import settings


class PaymentIntegration:
    @staticmethod
    async def generate_payment(payload: dict):
        url = 'https://api.mercadopago.com/v1/orders'

        headers = {
            "Authorization": f"Bearer {settings.MERCADO_PAGO_TOKEN}",
            "X-Idempotency-Key": str(uuid.uuid4()), 
            "Content-Type": "application/json" 
        }

        payment_data = {
            "total_amount": payload.get("total_amount"),
            "type": "online",
            "external_reference": str(payload.get("checkout_group_id")),
            "processing_mode": "automatic",
            "description": "Compra no Ateliê Digital",
            "transactions": {
                "payments": [
                    {
                        "amount": payload.get("total_amount"),
                        "payment_method": {
                            "id": "pix",
                            "type": "bank_transfer"
                        },
                        "expiration_time": "P3Y6M4DT12H30M5S" # Nota sobre isso abaixo
                    }
                ]
            },
            "payer": {
                "first_name": payload.get("buyer_first_name"),
                "last_name": payload.get("buyer_last_name"),
                "email": payload.get("buyer_email")
            }
        }


        async with AsyncClient() as client:
            try:
                response = await client.post(url, json=payment_data, headers=headers)
                response.raise_for_status()
                
                return response.json()
            except HTTPError as exc:
                if hasattr(exc, 'response') and exc.response is not None:
                    print(f"Detalhe do erro: {exc.response.json()}")
                
                return {}

    @staticmethod
    async def verify_payment(payment_id: str):
        url = f"https://api.mercadopago.com/v1/orders/{payment_id}"

        headers = {
            "Authorization": f"Bearer {settings.MERCADO_PAGO_TOKEN}",
            "Content-Type": "application/json" 
        }

        async with AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
            
            except HTTPError as exc:
                print(f"Erro ao verificar pagamento {payment_id} no Mercado Pago: {exc}")
                return {}