from typing import List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class Cart(Base, TimestampMixin):
    __tablename__ = 'cart'

    cart_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates='cart', cascade='all, delete-orphan')

class CartItem(Base):
    __tablename__ = 'cart_items'

    cart_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.cart_id"), nullable=False)
    product_variant_id: Mapped[str] = mapped_column(String(50), nullable=False)
    store_id: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart: Mapped['Cart'] = relationship(back_populates='items')
