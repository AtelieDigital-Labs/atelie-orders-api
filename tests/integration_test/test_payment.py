import asyncio
from app.integrations.payment_integration import PaymentIntegration


async def payment():

    payment_payload = {
        "total_amount": "1.00",
        "payment_method": "pix",
        "checkout_group_id": 12456,
        "buyer_email": "g.renata@testuser.com",
        "buyer_first_name": "Renata",
        "buyer_last_name": "Gomes",
    }

    print('Iniciando a requisição para realizar um pix...')

    try:
        result = await PaymentIntegration.generate_payment(payment_payload)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")


async def verify():
    payment_id = 'ORDTST01KRYP4R3YZEND3J6G9FWDWMQ3'

    print('Iniciando a requisição para verificar o status do pagamento')

    try:
        result = await PaymentIntegration.get_merchant_order(payment_id)
        print("Sucesso! Dados retornados:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste {e}")



if __name__ == "__main__":
    # print("Teste - Pagamento via pix")
    # asyncio.run(payment())
    print("Teste - Status de pagamento")
    asyncio.run(verify())


