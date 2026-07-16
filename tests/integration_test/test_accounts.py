import asyncio
from app.integrations.accounts_integration import AccountsIntegration


async def data_user():
    TOKEN_REAL = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc4MjAxMjMwLCJpYXQiOjE3NzgxOTc2MzAsImp0aSI6IjcxYTFmOGFkY2JlYjRiMDhhZmM2Mzk3OTlmOGFkNzg4IiwidXNlcl9pZCI6IjIifQ.0m1LNn53rAjqaZEj4Q39HOPsKQ0vqV_RRIudc7AL6I8'

    print('Iniciando a requisição para pegar os dados do usuário no Accounts...')

    try:
        result = await AccountsIntegration.get_data_user(TOKEN_REAL)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")

async def get_financials():
    user_id = 1

    print('Iniciando a requisição para pegar a chave pix no Accounts...')
    try:
        result = await AccountsIntegration.get_financials(user_id)
        print("Sucesso!!Dados retornados")
        print(result)

    except Exception as e:
        print(f"Erro durante o teste {e}")

async def get_address():
    address_id = "2"
    TOKEN_REAL = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc4MjAxMjMwLCJpYXQiOjE3NzgxOTc2MzAsImp0aSI6IjcxYTFmOGFkY2JlYjRiMDhhZmM2Mzk3OTlmOGFkNzg4IiwidXNlcl9pZCI6IjIifQ.0m1LNn53rAjqaZEj4Q39HOPsKQ0vqV_RRIudc7AL6I8'

    print('Iniciando a requisição para pegar os dados do endereço no Accounts...')


    try:
        result = await AccountsIntegration.get_address(address_id, TOKEN_REAL)
        print("Sucesso!!Dados retornados")
        print(result)
        
    except Exception as e:
        print(f"Erro durante o teste {e}")

if __name__ == "__main__":
    print("Teste - Dados do usuário")
    asyncio.run(data_user())
    print("-----------------")
    print("Teste - Chave pix")
    asyncio.run(get_financials())
    print("-----------------")
    print("Teste - Endereço")
    asyncio.run(get_address())

