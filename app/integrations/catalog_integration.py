from httpx import AsyncClient, HTTPError
from asyncio import gather
from fastapi import HTTPException
from http import HTTPStatus

class CatalogIntegration:
    @staticmethod
    async def get_store_zip(store_id: str):
        base_url = 'http://127.0.0.1:8000/api/catalog/store'
        
        async with AsyncClient(base_url=base_url) as client:
            try:
                response = await client.get(f'/{store_id}')
                
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND, 
                        detail=f'Loja {store_id} não encontrada.'
                    )
                    
                response.raise_for_status()
                data = response.json()
                
                # Acessa o dicionário 'address' e depois pega o 'zip_code' 
                address_data = data.get('address', {})
                zip_code = address_data.get('zip_code')
                
                if not zip_code:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, 
                        detail=f'A loja {store_id} não possui um CEP de origem válido cadastrado.'
                    )
                    
                return zip_code

            except HTTPError as exc:
                print(f'Erro ao conectar com o Catalog na busca da loja: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de catálogo indisponível no momento')


    @staticmethod
    async def search_price(client: AsyncClient, product_variant_id: str):
        response = await client.get(f'/{product_variant_id}')

        response.raise_for_status()

        unit_price = response.json().get('unit_price')
        stock = response.json().get('stock')
        weight = response.json().get('weight')
        height = response.json().get('height')
        width = response.json().get('width')
        length = response.json().get('length')


        return (product_variant_id, {'price': unit_price, 'stock': stock, 'weight':weight, 'height':height, 'width': width, 'length': length})

    @staticmethod
    async def fetch_all_prices(products_variants: list[str]):
        async with AsyncClient(base_url='https://127.0.0.1:8000/api/catalog/product') as client:
            try:
                tasks = [CatalogIntegration.search_price(client, variant_id) for variant_id in products_variants]

                results = await gather(*tasks)

                return dict(results)

            except HTTPError as exc:
                print(f'Erro ao conectar com o Catalog: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de catálogo indisponível')
            
            