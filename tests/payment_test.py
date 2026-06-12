import asyncio
from app.integrations.payment_integration import PaymentIntegration
from app.core.config import settings

# Substitua por um Access Token válido de teste do Mercado Pago
MERCADO_PAGO_TEST_TOKEN = settings.MERCADO_PAGO_TOKEN

async def test_payment(integration: PaymentIntegration):
    payment_payload = {
        "total_amount": "1.00", 
        "payment_method": "pix",
        "checkout_group_id": 12456,
        "buyer_email": "g.renata@testuser.com",
        "buyer_first_name": "Renata",
        "buyer_last_name": "Gomes",
        "items": [
            {
                "title": "laço",
                "quantity": 1,
                "unit_price": 1.00
            }
        ]
    }

    print('\n[1/2] Iniciando a requisição para realizar um pix...')

    try:
        result = await integration.generate_payment(payload=payment_payload)
        print("Sucesso! Dados retornados:")
        print(result)

        order_id = result.get("id") if result else None
        return order_id
    
    except Exception as e:
        print(f"Erro durante o teste de criação: {e}")
        return None


async def verify(integration: PaymentIntegration, payment_id: str):
    print(f'\n[2/2] Iniciando a requisição para verificar o status do pagamento ID: {payment_id}')

    try:
        result = await integration.get_merchant_order(payment_id)
        print("Sucesso! Dados retornados da consulta:")
        print(result)
    
    except Exception as e:
        print(f"Erro durante o teste de verificação: {e}")


async def run_all_tests():
    print("=== Iniciando Testes de Integração (Mercado Pago) ===")
    
    integration = PaymentIntegration(token=MERCADO_PAGO_TEST_TOKEN)
    
    created_payment_id = await test_payment(integration)
    
    if created_payment_id:
        await asyncio.sleep(1) 
        await verify(integration, str(created_payment_id))
    else:
        print("\n[Aviso] Verificação pulada pois o ID do pagamento não foi gerado.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())