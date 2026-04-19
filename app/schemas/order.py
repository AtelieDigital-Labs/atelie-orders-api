from pydantic import BaseModel
from decimal import Decimal
import datetime
from app.models.order import OrderStatus


# ORDER ITEM

class OrderItemCreate(BaseModel):
    product_variant_id: str
    quantity: int

    class Config():
        from_attributes = True 

class OrderItemRead(BaseModel):
    item_id: int
    product_variant_id: str
    quantity: int
    unit_price: Decimal

    class Config():
        from_attributes = True

# ORDER

class OrderCreate(BaseModel):
    store_id: str
    items: list[OrderItemCreate]

    class Config():
        from_attributes = True 


class OrderRead(BaseModel):
    order_id: int
    status: OrderStatus
    price: Decimal
    store_id: str
    created_at: datetime
    items: list[OrderItemRead]

    class Config():
        from_attributes = True 

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

    class Config():
        from_attributes = True 



