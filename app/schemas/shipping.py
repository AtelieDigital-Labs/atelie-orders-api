from pydantic import BaseModel
from decimal import Decimal
from typing import Dict

class ShippingOption(BaseModel):
    name: str # Ex: "Econômico" ou "Expresso"
    total_price: Decimal # A soma (Loja A + Loja B)
    max_delivery_time: int # O maior prazo entre as lojas
    stores_breakdown: Dict[str, Decimal] # O mapa {"loja_a": 12.00, "loja_b": 18.00}

class CartShippingResponse(BaseModel):
    cheapest: ShippingOption
    fastest: ShippingOption