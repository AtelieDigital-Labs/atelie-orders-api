from sqlalchemy.orm import Session
from models.order import Order, OrderItem

class OrderRepository:
    @staticmethod
    def create_order(session: Session, user_id: str, store_id: str, price: float):
        new_order = Order(
            user_id=user_id,
            store_id=store_id,
            price=price
        )
        
        session.add(new_order)
        session.flush()
        
        return new_order
    
    @staticmethod
    def create_order_items(session: Session, items_data: OrderItem):
        session.add_all(items_data)
        session.flush()