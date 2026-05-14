from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# CART ITEM

class CartItemCreate(BaseModel):
    """Schema para quando o usuário adiciona um item ao carrinho."""
    product_variant_id: str
    quantity: int = Field(gt=0, description="A quantidade deve ser maior que zero")

class CartItemUpdate(BaseModel):
    """Schema para atualizar a quantidade de um item no carrinho."""
    quantity: Optional[int] = None


class CartItemRead(BaseModel):
    """Schema para ler os dados do carrinho."""
    product_variant_id: str
    store_id: str
    quantity: int


