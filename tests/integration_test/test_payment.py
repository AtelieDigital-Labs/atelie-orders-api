import asyncio
from app.integrations.payment_integration import PaymentIntegration

MERCADO = 'APP_USR-5619885490238631-050516-b3e7114bf83014013078286744156ea1-3381554054'

integration = PaymentIntegration(token=MERCADO)


async def test_payment():
    payment_payload = {
        "total_amount": "1.00", 
        "payment_method": "pix",
        "checkout_group_id": 12456,
        "buyer_email": "g.renata@testuser.com",
        "buyer_first_name": "Renata",
        "buyer_last_name": "Gomes"
    }

    print('\n[1/2] Iniciando a requisição para realizar um pix...')

    try:
        # Agora chamamos a partir da instância
        result = await integration.generate_payment(payload=payment_payload)
        print("Sucesso! Dados retornados:")
        print(result)
        
        order_id = result.get("id") if result else None
        return order_id
    
    except Exception as e:
        print(f"Erro durante o teste de criação: {e}")
        return None


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
    print("Teste - Pagamento via pix")
    asyncio.run(test_payment())
    # print("Teste - Status de pagamento")
    # asyncio.run(verify())


