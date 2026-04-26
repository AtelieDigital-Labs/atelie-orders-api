from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

# CART ITEM

class CartItemCreate(BaseModel):
    """Schema para quando o usuário adiciona um item ao carrinho."""
    product_variant_id: str
    quantity: int

class CartItemUpdate(BaseModel):
    """Schema para atualizar a quantidade de um item no carrinho."""
    quantity: Optional[int] = None


class CartItemRead(BaseModel):
    cart_item_id: int
    cart_id: int
    product_variant_id: str
    store_id: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)

# CART 

class CartCreate(BaseModel):
    """Schema para iniciar um novo carrinho"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class CartUpdate(BaseModel):
    """Schema para vincular um session_id a um user_id (ex: após login)."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class CartRead(BaseModel):
    """Schema de saída do carrinho completo, incluindo os itens."""
    cart_id: int
    
    items: List[CartItemRead] = []
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)