import datetime
import enum
from decimal import Decimal
from typing import List
from sqlalchemy import create_engine, Integer, Enum, DateTime, DECIMAL, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base, TimestampMixin

    
class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = 'PAID',
    PROCESSING = "PROCESSING"
    SHIPPED = 'SHIPPED'
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    
    # Para o caso de ser impresso em um e-mail ou PDF
    @property
    def label(self) -> str:
        labels = {
            "PENDING": "Pendente",
            "PAID": "Pago", # verificar se a api precisa desse status
            "PROCESSING": "Em processamento",
            "SHIPPED": "Enviado", # Depende se terá a parte de frete
            "DELIVERED": "Entregue",
            "CANCELLED": "Cancelado"
        }
        return labels[self.value]
    
class Order(Base, TimestampMixin):
    __tablename__ = 'orders'
    
    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)    
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)    
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0.00"))

    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order") 

class OrderItem(Base, TimestampMixin):
    __tablename__ = 'order_items'

    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_variant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id", ondelete="CASCADE"))

    order: Mapped["Order"] = relationship(back_populates="items")
    
