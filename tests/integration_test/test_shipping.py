import asyncio
from app.integrations.shipping_integration import ShippingIntegration

async def success():

    print('Iniciando a requisição para calcular os fretes disponíveis')

    origin_zip = '76901-222'
    destinate_zip = '53437-848'

    payload = {
        "id": 1,
        "width": 20,
        "height": 30,
        "length": 60,
        "weight": 5,
        "insurance_value": 10,
        "quantity": 2
    }

    try:
        result = await ShippingIntegration.calculate_store_freight(origin_zip, destinate_zip, payload)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")



if __name__ == "__main__":
    # print("Teste - Pagamento via pix")
    # asyncio.run(payment())
    print("Teste - Status de pagamento")
    asyncio.run(success())