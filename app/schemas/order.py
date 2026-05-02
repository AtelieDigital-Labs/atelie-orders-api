from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from typing import Dict

from app.models.order import OrderStatus

# ORDER ITEM

class OrderItemCreate(BaseModel):
    store_id: str
    product_variant_id: str
    quantity: int

class OrderItemRead(BaseModel):
    item_id: int
    product_variant_id: str
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)

# ORDER
class OrderCheckoutRequest(BaseModel):
    address_id: str
    payment_method: str

    shipping_method: str = Field(..., description="Nome da opção de frete escolhida (ex: Econômico, Expresso).")
    shipping_costs_per_store: Dict[str, Decimal] = Field(
        ..., 
        description="Mapa contendo o ID da loja e o valor do frete específico para ela (ex: {'loja1': 15.50, 'loja2': 20.00})."
    )

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
    
class OrderCreatedResponse(BaseModel):
    message: str
    orders_id: list[int]


class OrderRead(BaseModel):
    order_id: int
    status: OrderStatus
    price: Decimal
    store_id: str
    created_at: datetime
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus




