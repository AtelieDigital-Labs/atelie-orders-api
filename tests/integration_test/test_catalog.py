import asyncio
from app.integrations.catalog_integration import CatalogIntegration


async def get_store_owner():
    store_id = '1'

    print('Iniciando a requisição para pegar os dados da loja...')

    try:
        result = await CatalogIntegration.get_store_owner(store_id)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")

async def fetch_all_products():
    print('Iniciando a requisição para pegar os dados dos produtos...')

    products_variants = ['1']

    try:
        result = await CatalogIntegration.fetch_all_products(products_variants)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")

async def get_store_id():
    print('Iniciando a requisição para pegar os dados da loja do artesão...')

    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc5MTQwMjU0LCJpYXQiOjE3NzkxMzY2NTQsImp0aSI6IjJmNTkyZTJkNzIwZDQ3ZmJiNjU5NGNlMWI3Yjg0YjM5IiwidXNlcl9pZCI6IjQifQ.ZKe4lI3KDoE0RAE_6qapNyPDF7LZEVLeXtF4JaxFlYY'
    try:
        result = await CatalogIntegration.get_store_id(token)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")

async def get_store_zip():
    print('Iniciando a requisição para pegar os dados do endereço do artesão...')

    store_id = '1'

    try:
        result = await CatalogIntegration.get_store_zip(store_id)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")

async def fetch_all_prices():
    print('Iniciando a requisição para pegar os dados do endereço do artesão...')

    products_variants = ['1']

    try:
        result = await CatalogIntegration.fetch_all_prices(products_variants)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")


if __name__ == "__main__":
    print("Teste - Dados da loja")
    # asyncio.run(get_store_owner())
    print("-----------------")
    print("Teste - Dados dos produtos para o carrinho")
    # asyncio.run(fetch_all_products())
    print("-----------------")
    print("Teste - Dados da loja do artesão")
    #asyncio.run(get_store_id())
    print("-----------------")
    print("Teste - Dados do endereço do artesão")
    # asyncio.run(get_store_zip())
    print("-----------------")
    print("Teste - Dados do produto para compra")
    asyncio.run(fetch_all_prices())
    print("-----------------")

