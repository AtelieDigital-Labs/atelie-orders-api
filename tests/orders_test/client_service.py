import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from http import HTTPStatus
from datetime import datetime, timezone
from decimal import Decimal
from fastapi_pagination import Page

# Importe a sua instância principal do FastAPI
from app.main import app 

from app.api.dependencies import verify_user
from app.core.database import get_session

# --- 1. CONFIGURAÇÃO DOS MOCKS E DEPENDÊNCIAS ---

# Simula um usuário logado retornando um ID fixo
def override_verify_user():
    return "user_abc123"

# Simula uma sessão de banco de dados vazia (não vamos usar o banco real)
async def override_get_session():
    yield None

# Sobrescreve as dependências no FastAPI apenas durante os testes
app.dependency_overrides[verify_user] = override_verify_user
app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

# --- 2. CLASSES FALSAS PARA O PYDANTIC (MOCKS) ---

class MockOrderItem:
    """Simula o modelo do SQLAlchemy de um item do pedido"""
    def __init__(self):
        self.item_id = 1
        self.product_variant_id = "variant_99"
        self.quantity = 2
        self.unit_price = Decimal("25.00")

class MockOrder:
    """Simula o modelo do SQLAlchemy de um pedido completo"""
    def __init__(self, order_id: int):
        self.order_id = order_id
        self.status = "PENDING"
        self.shipping_cost = Decimal("10.00")
        self.price = Decimal("50.00")
        self.store_id = "store_456"
        self.user_id = "user_abc123"
        self.created_at = datetime.now(timezone.utc)
        self.shipping_address = {
            "street": "Rua das Flores",
            "number": "123",
            "complement": "Apto 4",
            "neighborhood": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01000-000"
        }
        self.shipping_method = "expresso"
        self.payment_method = "pix"

        self.items = [MockOrderItem()]

# --- 3. OS TESTES REAIS ---

@patch("app.services.order_service.OrderService.get_order_by_id")
def test_get_order_by_id_success(mock_get_order_by_id):
    # Prepara o cenário: dizemos pro mock retornar o nosso pedido falso
    fake_order = MockOrder(order_id=105)
    mock_get_order_by_id.return_value = fake_order

    # Ação: Fazemos a requisição na rota
    response = client.get("/orders/105") # Ajuste o prefixo da rota se necessário

    print(f"\n--- DEBUG STATUS: {response.status_code} ---")
    print(f"--- DEBUG BODY: {response.json()} ---\n")

    # Verificações (Asserts)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["order_id"] == 105
    assert data["status"] == "PENDING"
    assert data["price"] == "50.00"
    assert data["shipping_address"]["city"] == "São Paulo"
    assert len(data["items"]) == 1


@patch("app.services.order_service.OrderService.get_order_by_id")
def test_get_order_by_id_not_found(mock_get_order_by_id):
    # Prepara o cenário: dizemos pro mock disparar a exceção 404 igual o seu código faz
    mock_get_order_by_id.side_effect = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, 
        detail="Pedido não encontrado ou não pertence a este usuário"
    )

    # Ação
    response = client.get("/orders/999")

    # Verificações
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Pedido não encontrado ou não pertence a este usuário"


@patch("app.services.order_service.OrderService.get_all_orders")
def test_get_all_orders_paginated(mock_get_all_orders):
    # Prepara o cenário: cria uma página falsa com 2 pedidos
    fake_order_1 = MockOrder(order_id=1)
    fake_order_2 = MockOrder(order_id=2)
    
    # Criamos o objeto Page da biblioteca fastapi-pagination que o seu service retornaria
    fake_page = Page(
        items=[fake_order_1, fake_order_2],
        total=2,
        page=1,
        size=50,
        pages=2
    )
    mock_get_all_orders.return_value = fake_page

    # Ação
    response = client.get("/orders/")

    # Verificações
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    
    # Valida a estrutura da paginação
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    
    # Valida o conteúdo
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["order_id"] == 1
    assert data["items"][1]["order_id"] == 2