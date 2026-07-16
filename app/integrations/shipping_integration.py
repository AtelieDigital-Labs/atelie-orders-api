from httpx import AsyncClient, HTTPError
from fastapi import HTTPException
from app.core.config import settings
 
class ShippingIntegration:
    def __init__(self, token: str, base_url: str = 'https://sandbox.melhorenvio.com.br/api/v2'):
        self.token = token
        self.base_url = base_url

    async def calculate_store_freight(self, origin_zip: str, dest_zip: str, products_payload: list) -> list:
        url = f'{self.base_url}/me/shipment/calculate'
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "AtelieDigital/1.0 (g.renata@escolar.ifrn.edu.br)" 
        }
        
        payload = {
            "from": {"postal_code": origin_zip},
            "to": {"postal_code": dest_zip},
            "products": products_payload
        }
        
        async with AsyncClient() as client:
            try:
                response = await client.post(url=url, json=payload, headers=headers)
                response.raise_for_status()
                
                return response.json()
            except HTTPError as exc:
                print(f"Erro ao cotar frete no Melhor Envio: {exc}")
                return []