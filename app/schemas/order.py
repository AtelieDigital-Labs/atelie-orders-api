from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Dict, Optional, Union

from app.models.order import OrderStatus


class ShippingAddressRead(BaseModel):
    street: str
    number: Union[str, int]
    complement: Optional[str] = None
    neighborhood: str
    city: str
    state: str
    zip_code: str

class OrderItemRead(BaseModel):
    item_id: int
    product_variant_id: str
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)

#
#   CLIENT
#

class OrderCheckoutRequest(BaseModel):
    address_id: str
    payment_method: str
    shipping_method: str = Field(..., description="Nome da opção de frete escolhida (ex: Econômico, Expresso).")    

class OrderCreatedResponse(BaseModel):
    message: str
    checkout_group_id: str
    payment_info: dict


class OrderRead(BaseModel):
    order_id: int
    status: OrderStatus
    price: Decimal
    shipping_cost: Decimal      
    shipping_method: str       
    tracking_code: Optional[str] = None
    payment_method: str
    store_id: str
    created_at: datetime
    shipping_address: ShippingAddressRead
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    order_id: int
    status: OrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 
#   ARTISAN
#

class OrderArtisanResponse(BaseModel):
    order_id: int
    status: OrderStatus
    price: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderArtisanRead(BaseModel):
    order_id: int
    status: OrderStatus
    price: Decimal
    created_at: datetime
    shipping_cost: Decimal
    shipping_method: str
    shipping_address: ShippingAddressRead
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)

class OrderArtisanStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_code: Optional[str] = Field(None, description="Obrigatório se o status for SHIPPED")

    @model_validator(mode='after')
    def check_tracking_code(self):
        if self.status == OrderStatus.SHIPPED and not self.tracking_code:
            raise ValueError("O código de rastreio é obrigatório para o status ENVIADO.")
        return self