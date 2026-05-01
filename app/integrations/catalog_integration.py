from httpx import AsyncClient, HTTPError
from asyncio import gather
from fastapi import HTTPException

class CatalogIntegration:
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
                raise HTTPException(status_code=503, detail='Serviço de catálogo indisponível')
            
            