import os
from httpx import AsyncClient, HTTPError
from fastapi import HTTPException

class ShippingIntegration:
    @staticmethod
    async def calculate_store_freight(origin_zip: str, dest_zip: str, products_payload: list) -> list:
        url = "https://www.melhorenvio.com.br/api/v2/me/shipment/calculate"
        
        headers = {
            "Authorization": f"Bearer {os.getenv('MELHOR_ENVIO_TOKEN')}",
            "Content-Type": "application/json",
            "User-Agent": "AtelieDigital/1.0 (g.renata@escolar.ifrn.edu.br)" # Eles exigem um User-Agent
        }
        
        payload = {
            "from": {"postal_code": origin_zip},
            "to": {"postal_code": dest_zip},
            "products": products_payload
        }
        
        async with AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                return response.json()
            except HTTPError as exc:
                print(f"Erro ao cotar frete no Melhor Envio: {exc}")
                return []