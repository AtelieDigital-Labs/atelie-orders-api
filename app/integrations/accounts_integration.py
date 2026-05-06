from httpx import AsyncClient, HTTPError
from asyncio import gather
from fastapi import HTTPException
from http import HTTPStatus

class AccountsIntegration:
    @staticmethod
    # passar o token no headers 
    async def get_data_user(user_id: str):
        # Verificar a rota, porque essa /me é quando ele está logado, e preciso ver o que passar visto que não achei rota pra pegar os dados de um usuário
        async with AsyncClient(base_url="https://localhost:800/api/accounts/me") as client:
            try:
                response = await client.get(f'/{user_id}/')

                response.raise_for_status()

                data = {
                    "email": response.json().get('email'),
                    "first_name": response.json().get('first_name'),
                    "last_name": response.json().get('last_name')
                }

                return data

            except HTTPError as exc:
                print(f'Erro ao conectar com o Accounts: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de autenticação indisponível')

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

                pix_key = response.json().get('pix_key')
                
                return pix_key

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