import pytest
from unittest.mock import patch, AsyncMock
from app.services.order_service import OrderService
from app.schemas.order import OrderCheckoutRequest

@pytest.mark.asyncio
# Nós "interceptamos" as classes de integração para elas não fazerem requisições HTTP reais
@patch('app.integrations.accounts_integration.AccountsIntegration.get_address')
@patch('app.integrations.catalog_integration.CatalogIntegration.fetch_all_prices')
@patch('app.services.cart_service.CartService.get_cart_items')
@patch('app.services.cart_service.CartService.clear_cart')
@patch('app.repositories.order_repository.OrderRepository.create_order')
@patch('app.repositories.order_repository.OrderRepository.create_order_items')
async def test_create_new_order_success(
    mock_create_items, mock_create_order, mock_clear_cart, 
    mock_get_cart, mock_fetch_prices, mock_get_address
):
    # 1. PREPARANDO O CENÁRIO (Fingindo o retorno das APIs)
    
    # Simulando o retorno do Accounts
    mock_get_address.return_value = {
        "user_id": "user_teste",
        "street": "Rua Fake", "number": "123", "zip_code": "00000-000",
        "neighborhood": "Bairro", "city": "Cidade", "state": "UF"
    }

    # Simulando que temos 1 item no carrinho
    mock_cart_item = AsyncMock()
    mock_cart_item.product_variant_id = "var_1"
    mock_cart_item.store_id = "store_123"
    mock_cart_item.quantity = 2
    mock_get_cart.return_value = [mock_cart_item]

    # Simulando o retorno do Catalog com preço e estoque
    mock_fetch_prices.return_value = {
        "var_1": {"unit_price": 50.00, "stock": 10}
    }

    # Simulando a criação da Ordem no banco (Mockando o ID gerado)
    mock_new_order = AsyncMock()
    mock_new_order.order_id = 999
    mock_create_order.return_value = mock_new_order

    # 2. EXECUTANDO A AÇÃO
    # Criando o payload de mentira do front-end
    request_data = OrderCheckoutRequest(
        address_id="1",
        payment_method="PIX",
        shipping_method="Correios PAC",
        shipping_costs_per_store={"store_123": 20.00}
    )
    
    # Chamando o seu Service de verdade!
    result = await OrderService.create_new_order(
        order_data=request_data, 
        session=AsyncMock(), # Sessão do banco fake
        user_id="user_teste"
    )

    # 3. VERIFICANDO OS RESULTADOS (Asserts)
    assert result['message'] == 'Pedido gerado'
    assert result['orders_id'] == [999]
    
    # Garantindo que o carrinho foi limpo no final
    mock_clear_cart.assert_called_once()
    
    # Garantindo que a ordem foi criada com os dados certos
    mock_create_order.assert_called_once()
    args, kwargs = mock_create_order.call_args
    assert kwargs['price'] == 100.00 # (2 quantidades x 50 reais)
    assert kwargs['shipping_cost'] == 20.00