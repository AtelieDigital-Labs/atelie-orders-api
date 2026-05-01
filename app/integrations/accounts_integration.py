from httpx import AsyncClient, HTTPError
from asyncio import gather
from fastapi import HTTPException

class AccountsIntegration:
    @staticmethod
    async def get_address(address_id: str):
        async with AsyncClient(base_url="https://localhost:800/api/accounts/address") as client:
            try:
                response = await client.get(f'/{address_id}')

                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                
                return response.json()

            except HTTPError as exc:
                print(f'Erro ao conectar com o Accounts: {exc}')
                raise HTTPException(status_code=503, detail='Serviço de autenticação indisponível')