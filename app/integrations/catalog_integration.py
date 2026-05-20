from httpx import AsyncClient, HTTPError
from asyncio import gather
from fastapi import HTTPException
from http import HTTPStatus
 
class CatalogIntegration:
    @staticmethod
    async def get_store_owner(store_id: str):
        base_url = 'http://catalog_api:8008/api/v1/catalog/stores'

        async with AsyncClient(base_url=base_url) as client:
            try:
                response = await client.get(f'/{store_id}/artisan')

                
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND, 
                        detail=f'Loja {store_id} não encontrada.'
                    )
                    
                response.raise_for_status()

                response_data = response.json()

                store_owner = response_data.get('artisan_id')

                return store_owner

            except HTTPError as exc:
                print(f'Erro ao conectar com o Catalog na busca do dono da loja: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de catálogo indisponível no momento')
            
    @staticmethod
    async def get_data_for_product(client: AsyncClient, product_variant_id: str):
        response = await client.get(f'/{product_variant_id}')

        response.raise_for_status()

        payload = response.json()

        store_id = str(payload.get('store_id'))
        unit_price = payload.get('price')
        stock = payload.get('stock')
    

        return (product_variant_id, {'store_id': store_id, 'unit_price': unit_price, 'stock': stock})

    
    @staticmethod
    async def fetch_all_products(products_variants: list[str]):
        async with AsyncClient(base_url='http://catalog_api:8008/api/v1/catalog/products/variations') as client:
            
            tasks = [CatalogIntegration.get_data_for_product(client, variant_id) for variant_id in products_variants]
            results = await gather(*tasks, return_exceptions=True)

            valid_data = {}
            
            for variant_id, result in zip(products_variants, results):
                if isinstance(result, Exception):
                    print(f"Erro ao buscar o produto {variant_id} no catálogo: {result}")
                    valid_data[variant_id] = {'store_id': 'default', 'unit_price': 0.0, 'stock': 0}
                else:
                    valid_data[variant_id] = result[1]

            return valid_data

    @staticmethod
    async def get_store_id(token: str):
       
        base_url = 'http://catalog_api:8008/api/v1/catalog/stores/me'

        headers = {
            "Authorization": f"Bearer {token}"  
        }

        async with AsyncClient() as client:
            try:
                response = await client.get(url=base_url,headers=headers)

                if response.status_code == 404:
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Loja não encontrada')
                
                response.raise_for_status()

                data = response.json()

                store_id = data.get('id')

                return store_id
            
            except HTTPError as exc:
                print(f'Erro ao conectar com o Catalog na busca da loja: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de catálogo indisponível no momento')
            

    @staticmethod
    async def get_store_zip(store_id: str):
        base_url = 'http://catalog_api:8008/api/v1/catalog/stores'
        
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

        data = response.json()
        
        unit_price = data.get('price')
        stock = data.get('stock')
        weight = data.get('weight')
        height = data.get('height')
        width = data.get('width')
        length = data.get('length')

        return (product_variant_id, {'unit_price': unit_price, 'stock': stock, 'weight':weight, 'height':height, 'width': width, 'length': length})

    @staticmethod
    async def fetch_all_prices(products_variants: list[str]):
        async with AsyncClient(base_url='http://catalog_api:8008/api/v1/catalog/products/variations') as client:
            try:
                tasks = [CatalogIntegration.search_price(client, variant_id) for variant_id in products_variants]

                results = await gather(*tasks)

                return dict(results)

            except HTTPError as exc:
                print(f'Erro ao conectar com o Catalog: {exc}')
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail='Serviço de catálogo indisponível')
    
    # Método para ir posterior por RabbitMQ
    @staticmethod
    async def deacrese_stock(paylod: list[dict]):
        url = 'http://catalog_api:8008/api/v1/catalog/stock/decrease'

        async with AsyncClient() as client:
            try:
                response = await client.post(url, json=paylod)
                response.raise_for_status()
                return True
            except HTTPError as exc:
                print(f'Erro ao tentar baixar estoque no Catalog: {exc}')
                return False