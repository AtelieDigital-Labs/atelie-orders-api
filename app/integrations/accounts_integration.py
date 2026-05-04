from httpx import AsyncClient, HTTPError
from asyncio import gather
from fastapi import HTTPException
from http import HTTPStatus

class AccountsIntegration:
    @staticmethod
    async def get_financials(user_id: str):
        # ajustar base_url conforme o accounts
        async with AsyncClient(base_url="https://localhost:800/api/accounts/") as client:
            try:
                response = await client.get(f'/{user_id}/financials')

                if response.status_code == 404:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND, 
                        detail=f'Essa loja não possui chave financeira.'
                    )
                
                response.raise_for_status()

                mp_receiver_id = response.json().get('mp_receiver_id')
                
                return mp_receiver_id

            except HTTPError as exc:
                print(f'Erro ao conectar com o Accounts: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de autenticação indisponível')
            
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
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de autenticação indisponível')