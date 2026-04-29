import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

# Importe o Service que vamos testar
from app.services.order_service import OrderService

class DummyCartItem:
    def __init__(self, variant_id, qty, store_id):
        self.product_variant_id = variant_id
        self.quantity = qty
        self.store_id = store_id

class DummyOrder:
    def __init__(self, order_id):
        self.order_id = order_id

@pytest.mark.asyncio
async def test_create_new_order_cart_empty(mocker):
    
    # ==========================================
    # ARRANGE (Preparação dos Dados)
    # ==========================================
    user_id = "user_123"
    
    # Criamos um "dublê" para a sessão do banco. 
    # Ele aceita receber "awaits" sem tentar conectar no Postgres de verdade.
    session_mock = AsyncMock() 

    # Dizemos: "Quando o OrderService tentar chamar o get_cart, não vá no banco! Apenas retorne None"
    mocker.patch(
        'app.services.order_service.CartService.get_cart_items',
        return_value=None # Simulando que não achou o carrinho
    )

    # ==========================================
    # ACT & ASSERT (Ação e Validação)
    # ==========================================
    
    # Como a nossa regra de negócio manda "levantar um erro" se estiver vazio,
    # nós mandamos o pytest "esperar" (raises) que esse erro aconteça.
    with pytest.raises(HTTPException) as exc_info:
        await OrderService.create_new_order(session=session_mock, user_id=user_id)

    # 1. Validamos se o erro foi exatamente um 400
    assert exc_info.value.status_code == 400
    
    # 2. Validamos se a mensagem de erro foi a correta
    assert exc_info.value.detail == 'Não existem items no carrinho do usuário para prosseguir com a compra.'
    
    # Como simulamos um erro, garantimos que o Service limpou a transação do banco!
    session_mock.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_new_order_stock_scant(mocker):
    session_mock = AsyncMock()
    
    # Criamos a LISTA de itens diretamente
    fake_items = [DummyCartItem(variant_id="prod_A", qty=10, store_id="store_1")]
    
    mocker.patch('app.services.order_service.CartService.get_cart_items', return_value=fake_items)
    
    # Catalog diz que só tem 2 no estoque
    fake_catalog = {"prod_A": {"unit_price": 10.0, "stock": 2}}
    mocker.patch('app.services.order_service.CatalogIntegration.fetch_all_prices', return_value=fake_catalog)

    with pytest.raises(HTTPException) as exc_info:
        await OrderService.create_new_order(session=session_mock, user_id="user_1")

    assert exc_info.value.status_code == 400
    assert "Estoque insuficiente" in exc_info.value.detail

@pytest.mark.asyncio
async def test_create_new_order_success(mocker):
    session_mock = AsyncMock()
    
    fake_items = [DummyCartItem(variant_id="prod_A", qty=1, store_id="store_1")]
    
    mocker.patch('app.services.order_service.CartService.get_cart_items', return_value=fake_items)
    
    fake_catalog = {"prod_A": {"unit_price": 10.0, "stock": 100}}
    mocker.patch('app.services.order_service.CatalogIntegration.fetch_all_prices', return_value=fake_catalog)

    mocker.patch('app.services.order_service.OrderRepository.create_order', return_value=DummyOrder(order_id="order_123"))
    mocker.patch('app.services.order_service.OrderRepository.create_order_items', return_value=None)
    
    mocker.patch('app.services.order_service.CartService.clear_cart', return_value=None)

    result = await OrderService.create_new_order(session=session_mock, user_id="user_1")

    assert result['message'] == 'Pedido gerado'
    assert "order_123" in result['orders_id']
    session_mock.commit.assert_awaited_once()