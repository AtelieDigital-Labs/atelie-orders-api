import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

# Importe o Service e o Schema que vamos testar
from app.services.order_service import OrderService
from app.schemas.order import OrderCheckoutRequest

# ==========================================
# CLASSES E DADOS AUXILIARES (DUMMIES)
# ==========================================
class DummyCartItem:
    def __init__(self, variant_id, qty, store_id):
        self.product_variant_id = variant_id
        self.quantity = qty
        self.store_id = store_id

class DummyOrder:
    def __init__(self, order_id):
        self.order_id = order_id

# Um endereço falso válido para o usuário passar na validação de segurança
VALID_ADDRESS_MOCK = {
    "user": "user_123",
    "street": "Rua Lagoa Nova",
    "number": "1",
    "neighborhood": "XX",
    "city": "Agua Nova",
    "state": "RN",
    "zip_code": "0555-5550",
    "complement": "perto do parque"
}

# ==========================================
# TESTES
# ==========================================

@pytest.mark.asyncio
async def test_create_new_order_cart_empty(mocker):
    # 1. ARRANGE
    user_id = "user_123"
    session_mock = AsyncMock() 

    # Criando o payload que o front-end enviaria
    order_request = OrderCheckoutRequest(
        address_id="addr_1",
        payment_method="PIX",
        shipping_method="Econômico",
        shipping_costs_per_store={}
    )

    # Mockando a validação de endereço para passar com sucesso
    mocker.patch('app.services.order_service.AccountsIntegration.get_address', return_value=VALID_ADDRESS_MOCK)

    # Simulando que não achou o carrinho
    mocker.patch('app.services.order_service.CartService.get_cart_items', return_value=None)

    # 2. ACT & ASSERT
    with pytest.raises(HTTPException) as exc_info:
        # Agora passamos o order_data também
        await OrderService.create_new_order(order_data=order_request, session=session_mock, user_id=user_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == 'Não existem items no carrinho do usuário para prosseguir com a compra.'
    session_mock.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_new_order_stock_scant(mocker):
    # 1. ARRANGE
    user_id = "user_123"
    session_mock = AsyncMock()
    
    order_request = OrderCheckoutRequest(
        address_id="addr_1",
        payment_method="PIX",
        shipping_method="Econômico",
        shipping_costs_per_store={"store_1": 15.00}
    )

    mocker.patch('app.services.order_service.AccountsIntegration.get_address', return_value=VALID_ADDRESS_MOCK)
    
    fake_items = [DummyCartItem(variant_id="prod_A", qty=10, store_id="store_1")]
    mocker.patch('app.services.order_service.CartService.get_cart_items', return_value=fake_items)
    
    # Catalog diz que só tem 2 no estoque (cliente pediu 10)
    fake_catalog = {"prod_A": {"unit_price": 10.0, "stock": 2}}
    mocker.patch('app.services.order_service.CatalogIntegration.fetch_all_prices', return_value=fake_catalog)

    # 2. ACT & ASSERT
    with pytest.raises(HTTPException) as exc_info:
        await OrderService.create_new_order(order_data=order_request, session=session_mock, user_id=user_id)

    assert exc_info.value.status_code == 400
    assert "Estoque insuficiente para o produto prod_A" in exc_info.value.detail
    session_mock.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_new_order_success(mocker):
    # 1. ARRANGE
    user_id = "user_123"
    session_mock = AsyncMock()
    
    order_request = OrderCheckoutRequest(
        address_id="addr_1",
        payment_method="PIX",
        shipping_method="Econômico",
        shipping_costs_per_store={"store_1": 25.50}
    )

    # Validando endereço e carrinho
    mocker.patch('app.services.order_service.AccountsIntegration.get_address', return_value=VALID_ADDRESS_MOCK)
    fake_items = [DummyCartItem(variant_id="prod_A", qty=1, store_id="store_1")]
    mocker.patch('app.services.order_service.CartService.get_cart_items', return_value=fake_items)
    
    # Estoque suficiente e preço
    fake_catalog = {"prod_A": {"unit_price": 10.0, "stock": 100}}
    mocker.patch('app.services.order_service.CatalogIntegration.fetch_all_prices', return_value=fake_catalog)

    # Simulando o banco de dados salvando e limpando o carrinho
    mocker.patch('app.services.order_service.OrderRepository.create_order', return_value=DummyOrder(order_id="order_123"))
    mocker.patch('app.services.order_service.OrderRepository.create_order_items', return_value=None)
    mocker.patch('app.services.order_service.CartService.clear_cart', return_value=None)

    # 2. ACT
    result = await OrderService.create_new_order(order_data=order_request, session=session_mock, user_id=user_id)

    # 3. ASSERT
    assert result['message'] == 'Pedido gerado'
    assert "order_123" in result['orders_id']
    session_mock.commit.assert_awaited_once()