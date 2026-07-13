from httpx import AsyncClient, HTTPError
import uuid
from app.core.config import settings


class PaymentIntegration:
    def __init__(self, token: str, base_url: str = 'https://api.mercadopago.com/v1'):
        self.token = token
        self.base_url = base_url

    async def generate_payment(self, payload: dict):
        url = f'{self.base_url}/orders'

        headers = {
            "Authorization": f"Bearer {self.token}",
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
                            "type": "bank_transfer",
                            "statement_descriptor": "COMPRA NO ATELIÊ DIGITAL"
                        },
                        "expiration_time": "PT15M" 
                    }
                ]
            },
            "payer": {
                "first_name": payload.get("buyer_first_name"),
                "last_name": payload.get("buyer_last_name"),
                "email": payload.get("buyer_email")
            },
            "items": [
                {
                    "title": item.get("title"),
                    "quantity": item.get("quantity"),
                    "unit_price": str(item.get("unit_price")),
                }
                for item in payload.get("items", [])
            ]
        }


        async with AsyncClient() as client:
            try:
                response = await client.post(url=url, json=payment_data, headers=headers)
                response.raise_for_status()
                
                return response.json()
            except HTTPError as exc:
                if hasattr(exc, 'response') and exc.response is not None:
                    print(f"Detalhe do erro: {exc.response.json()}")
                
                return {}

    async def get_merchant_order(self, order_id: str):
        url = f'{self.base_url}/orders/{order_id}'

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json" 
        }

        async with AsyncClient() as client:
            try:
                response = await client.get(url=url, headers=headers)
                response.raise_for_status()
                return response.json()
            
            except HTTPError as exc:
                status_code = exc.response.status_code if hasattr(exc, 'response') else "Desconhecido"
                detalhes = exc.response.text if hasattr(exc, 'response') else str(exc)
                
                print(f"Erro {status_code} ao consultar a Ordem {order_id}")
                print(f"Detalhes do MP: {detalhes}")
                
                print(f"Erro ao verificar pagamento {order_id} no Mercado Pago: {exc}")
                return None