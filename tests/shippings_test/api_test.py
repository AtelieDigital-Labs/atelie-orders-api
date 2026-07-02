import pytest
from unittest.mock import patch, AsyncMock
from decimal import Decimal
from http import HTTPStatus

# Ajuste os imports abaixo de acordo com a estrutura de pastas do seu projeto
from app.services.shipping_service import ShippingService 
from app.schemas.shipping import CartShippingResponse

@pytest.mark.asyncio
async def test_calculate_cart_shipping_real_melhor_envio():
    """
    Testa o cálculo de frete batendo na API REAL do Melhor Envio.
    Mockamos o carrinho e o catálogo, mas deixamos a requisição de frete passar.
    """
    # 1. Arrange (Preparação)
    user_id = "test_user_123"
    destination_zip = "01001000"  # CEP de destino válido (Ex: Praça da Sé, SP)
    fake_redis = AsyncMock()      # Falso Redis, já que não vamos usá-lo de verdade

    # Simulando os dados que viriam do Redis/Carrinho
    mock_cart_data = {
        "items": [
            {
                "product_variant_id": "variant_1",
                "store_id": "store_1",
                "quantity": 1
            }
        ]
    }

    # Simulando os dados que viriam do microsserviço de Catálogo (Dimensões válidas)
    mock_catalog_data = {
        "variant_1": {
            "width": 15,
            "height": 15,
            "length": 15,
            "weight": 1.0,       # 1 Kg
            "unit_price": 100.0  # Valor do seguro
        }
    }

    origin_zip = "20040000"  # CEP de origem da loja válido (Ex: Centro do Rio de Janeiro)

    # Aplicando os Mocks apenas nos serviços internos
    with patch("app.services.cart_service.CartService.get_items", new_callable=AsyncMock) as mock_get_items, \
         patch("app.integrations.catalog_integration.CatalogIntegration.fetch_all_prices", new_callable=AsyncMock) as mock_fetch_prices, \
         patch("app.integrations.catalog_integration.CatalogIntegration.get_store_zip", new_callable=AsyncMock) as mock_get_zip:
        
        # Configurando os retornos dos mocks
        mock_get_items.return_value = mock_cart_data
        mock_fetch_prices.return_value = mock_catalog_data
        mock_get_zip.return_value = origin_zip
        
        # 2. Act (Ação)
        # ATENÇÃO: ShippingIntegration.calculate_store_freight NÃO está mockado!
        # Ele vai executar a chamada real para a API do Melhor Envio.
        response = await ShippingService.calculate_cart_shipping(
            redis=fake_redis, 
            user_id=user_id, 
            destination_zip=destination_zip
        )

        print("\n" + "="*50)
        print("🚛 RETORNO REAL DO MELHOR ENVIO (PROCESSADO)")
        print("="*50)
        print(f"OPÇÃO MAIS BARATA ({response.cheapest.name}):")
        print(f" - Preço Total: R$ {response.cheapest.total_price}")
        print(f" - Prazo Máximo: {response.cheapest.max_delivery_time} dias")
        print(f" - Divisão por Loja: {response.cheapest.stores_breakdown}")
        print("-" * 50)
        print(f"OPÇÃO MAIS RÁPIDA ({response.fastest.name}):")
        print(f" - Preço Total: R$ {response.fastest.total_price}")
        print(f" - Prazo Máximo: {response.fastest.max_delivery_time} dias")
        print(f" - Divisão por Loja: {response.fastest.stores_breakdown}")
        print("="*50 + "\n")
        
        # 3. Assert (Verificações)
        # Verifica se retornou o Schema correto
        assert isinstance(response, CartShippingResponse)
        
        # Como é uma chamada real, os preços exatos variam, 
        # então validamos se eles são maiores que zero e do tipo Decimal.
        assert isinstance(response.cheapest.total_price, Decimal)
        assert response.cheapest.total_price > Decimal("0.00"), "O preço do frete mais barato deve ser maior que zero"
        
        assert isinstance(response.fastest.total_price, Decimal)
        assert response.fastest.total_price > Decimal("0.00"), "O preço do frete mais rápido deve ser maior que zero"
        
        # Verifica se os prazos de entrega voltaram preenchidos
        assert response.cheapest.max_delivery_time > 0
        assert response.fastest.max_delivery_time > 0
        
        # Verifica o mapeamento por loja no breakdown
        assert "store_1" in response.cheapest.stores_breakdown
        assert "store_1" in response.fastest.stores_breakdown
        
        # Verifica a nomenclatura configurada no seu service
        assert "Econômico" in response.cheapest.name
        assert "Expresso" in response.fastest.name

        # Valida se o plano B de Retirada (Fallback) não foi ativado indevidamente (já que os CEPs são válidos)
        assert "Retirada obrigatória" not in response.cheapest.name