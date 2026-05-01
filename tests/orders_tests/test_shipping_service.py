import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from decimal import Decimal
from fastapi import HTTPException

# Ajuste os imports abaixo de acordo com a estrutura real das suas pastas
from app.services.shipping_service import ShippingService
from app.schemas.shipping import CartShippingResponse

# ==========================================
# 1. FUNÇÕES AUXILIARES PARA OS MOCKS (SIDE EFFECTS)
# ==========================================
# Usamos 'side_effect' para fazer a nossa função de mentira retornar 
# valores diferentes dependendo de qual loja está sendo pesquisada.

async def mock_get_store_zip_side_effect(store_id):
    zips = {
        "loja_A": "01000-000",
        "loja_B": "02000-000"
    }
    return zips.get(store_id, "00000-000")

async def mock_calculate_freight_side_effect(origin_zip, dest_zip, payload):
    # Se for a Loja A, o frete é mais barato e mais rápido
    if origin_zip == "01000-000": 
        return [
            {"name": "PAC", "price": "15.00", "delivery_time": 5},
            {"name": "SEDEX", "price": "30.00", "delivery_time": 2}
        ]
    # Se for a Loja B, o frete é mais caro e demora mais
    elif origin_zip == "02000-000": 
        return [
            {"name": "PAC", "price": "20.00", "delivery_time": 7},
            {"name": "SEDEX", "price": "45.00", "delivery_time": 3}
        ]
    return []

# ==========================================
# 2. OS CENÁRIOS DE TESTE
# ==========================================

@pytest.mark.asyncio
@patch('app.integrations.shipping_integration.ShippingIntegration.calculate_store_freight')
@patch('app.integrations.catalog_integration.CatalogIntegration.get_store_zip')
@patch('app.integrations.catalog_integration.CatalogIntegration.fetch_all_prices')
@patch('app.services.cart_service.CartService.get_cart_items')
async def test_calculate_cart_shipping_success(
    mock_get_cart, mock_fetch_prices, mock_get_store_zip, mock_calculate_freight
):
    """
    CENÁRIO 1: Sucesso. Calcula frete de duas lojas diferentes e soma os valores.
    """
    # 1. Preparando o Carrinho Fake (1 item da Loja A, 1 item da Loja B)
    item_a = MagicMock(product_variant_id="var_1", store_id="loja_A", quantity=1)
    item_b = MagicMock(product_variant_id="var_2", store_id="loja_B", quantity=2)
    mock_get_cart.return_value = [item_a, item_b]

    # 2. Preparando os Preços e Dimensões Fake no Catalog
    mock_fetch_prices.return_value = {
        "var_1": {"unit_price": 50.0, "width_cm": 10, "height_cm": 10, "length_cm": 10, "weight_kg": 0.5},
        "var_2": {"unit_price": 30.0, "width_cm": 20, "height_cm": 20, "length_cm": 20, "weight_kg": 1.0}
    }

    # 3. Configurando os retornos dinâmicos para o CEP e Melhor Envio
    mock_get_store_zip.side_effect = mock_get_store_zip_side_effect
    mock_calculate_freight.side_effect = mock_calculate_freight_side_effect

    # 4. Executando a função do Service
    # Matemática Esperada:
    # Econômico: Loja A (15.00) + Loja B (20.00) = 35.00 | Prazo: max(5, 7) = 7
    # Expresso: Loja A (30.00) + Loja B (45.00) = 75.00 | Prazo: max(2, 3) = 3
    
    response = await ShippingService.calculate_cart_shipping(
        session=AsyncMock(), 
        user_id="user_123", 
        destination_zip="59000-000"
    )

    # 5. Verificações (Asserts)
    assert isinstance(response, CartShippingResponse)
    
    # Validando a Opção Mais Barata (Econômico)
    assert response.cheapest.total_price == Decimal("35.00")
    assert response.cheapest.max_delivery_time == 7
    assert response.cheapest.stores_breakdown["loja_A"] == Decimal("15.00")
    assert response.cheapest.stores_breakdown["loja_B"] == Decimal("20.00")

    # Validando a Opção Mais Rápida (Expresso)
    assert response.fastest.total_price == Decimal("75.00")
    assert response.fastest.max_delivery_time == 3
    assert response.fastest.stores_breakdown["loja_A"] == Decimal("30.00")
    assert response.fastest.stores_breakdown["loja_B"] == Decimal("45.00")


@pytest.mark.asyncio
@patch('app.services.cart_service.CartService.get_cart_items')
async def test_calculate_cart_shipping_empty_cart(mock_get_cart):
    """
    CENÁRIO 2: Carrinho Vazio. Deve levantar HTTPException 400.
    """
    # Simulando banco de dados retornando array vazio
    mock_get_cart.return_value = []

    # O Pytest intercepta a exceção e confirma se ela foi gerada
    with pytest.raises(HTTPException) as exc_info:
        await ShippingService.calculate_cart_shipping(
            session=AsyncMock(), 
            user_id="user_123", 
            destination_zip="59000-000"
        )
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Carrinho vazio."


@pytest.mark.asyncio
@patch('app.integrations.shipping_integration.ShippingIntegration.calculate_store_freight')
@patch('app.integrations.catalog_integration.CatalogIntegration.get_store_zip')
@patch('app.integrations.catalog_integration.CatalogIntegration.fetch_all_prices')
@patch('app.services.cart_service.CartService.get_cart_items')
async def test_calculate_cart_shipping_api_error(
    mock_get_cart, mock_fetch_prices, mock_get_store_zip, mock_calculate_freight
):
    """
    CENÁRIO 3: Falha na API de Logística.
    Se a API do Melhor Envio retornar vazio para uma loja, o sistema deve interromper.
    """
    # 1. Preparando Carrinho (1 item da Loja A)
    item_a = MagicMock(product_variant_id="var_1", store_id="loja_A", quantity=1)
    mock_get_cart.return_value = [item_a]

    # 2. Preparando Preços
    mock_fetch_prices.return_value = {
        "var_1": {"unit_price": 50.0}
    }
    
    mock_get_store_zip.return_value = "01000-000"

    # 3. Forçando a API do Melhor Envio a retornar uma lista vazia (falha de área/CEP)
    mock_calculate_freight.return_value = []

    # 4. Verificando o Erro
    with pytest.raises(HTTPException) as exc_info:
        await ShippingService.calculate_cart_shipping(
            session=AsyncMock(), 
            user_id="user_123", 
            destination_zip="59000-000"
        )
    
    assert exc_info.value.status_code == 503
    assert "Erro ao cotar frete para a loja loja_A" in exc_info.value.detail