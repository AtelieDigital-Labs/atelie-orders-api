import enum
import uuid
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import DECIMAL, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID


from app.core.database import Base, TimestampMixin



class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = 'PAID'
    REFUSED = 'REFUSED'
    PROCESSING = "PROCESSING"
    SHIPPED = 'SHIPPED'
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    
    # Para o caso de ser impresso em um e-mail ou PDF
    @property
    def label(self) -> str:
        labels = {
            "PENDING": "Pendente",
            "PAID": "Pago", 
            "REFUSED": 'Recusado',
            "PROCESSING": "Em processamento",
            "SHIPPED": "Enviado", 
            "DELIVERED": "Entregue",
            "CANCELLED": "Cancelado"
        }
        return labels[self.value]
     
class Order(Base, TimestampMixin):
    __tablename__ = 'orders'
    
    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)    
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)    
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0.00"))
    platform_fee: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0.00"))
    artisan_ammount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0.00"))
    shipping_cost: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0.00"))

    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    shipping_address: Mapped[dict] = mapped_column(JSONB, nullable=False)
    shipping_method: Mapped[str] = mapped_column(String(100), nullable=False)
    tracking_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    checkout_group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order") 

class OrderItem(Base, TimestampMixin):
    __tablename__ = 'order_items'

    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_variant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id", ondelete="CASCADE"))

    order: Mapped["Order"] = relationship(back_populates="items")
    
