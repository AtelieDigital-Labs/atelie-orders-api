from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

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




