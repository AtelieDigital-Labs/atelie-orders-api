from httpx import AsyncClient, HTTPError
from asyncio import gather
from fastapi import HTTPException
from http import HTTPStatus

class AccountsIntegration:
    @staticmethod
    # passar o token no headers 
    async def get_data_user(token: str):

        base_url = "http://app:8001/api/accounts/me/" 
        
        headers = {
            "Authorization": f"Bearer {token}"  
        }

        async with AsyncClient() as client:
            try:
                response = await client.get(url=base_url, headers=headers)

                response.raise_for_status()

                response_data = response.json()

                data = {
                    "email": response_data.get('email'),
                    "first_name": response_data.get('first_name'),
                    "last_name": response_data.get('last_name')
                }

                return data

            except HTTPError as exc:
                print(f'Erro ao conectar com o Accounts: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de autenticação indisponível')

    @staticmethod
    async def get_financials(user_id: str, token: str):
        headers = {
            "Authorization": f"Bearer {token}"  
        }

        async with AsyncClient(base_url="http://app:8001/api/accounts/") as client:
            try:
                response = await client.get(f'/{user_id}/financials', headers=headers)

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
    async def get_address(address_id: str, token: str):
        
        headers = {
            "Authorization": f"Bearer {token}"  
        }

        async with AsyncClient(base_url = "http://app:8001/api/accounts/addresses/") as client:
            try:
                response = await client.get(f'/{address_id}/', headers=headers)

                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                
                return response.json()

            except HTTPError as exc:
                print(f'Erro ao conectar com o Accounts: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de autenticação indisponível')