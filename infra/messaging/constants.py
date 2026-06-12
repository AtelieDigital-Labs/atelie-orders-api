from enum import StrEnum

class Exchange(StrEnum):
    ACCOUNTS_EXCHANGE = "accounts.events"
    ORDER_EXCHANGE = "orders.events"
    CATALOG_EXCHANGE = "catalogs.events"

class Queue(StrEnum):
    USER_CREATED_QUEUE = "accounts.user.created.queue"
    WALLET_TRANSACTION_QUEUE = 'accounts.wallet.transaction.queue'
    BECOME_ARTISAN_QUEUE= "accounts.become.artisan.queue"
    CREATE_WALLET_QUEUE= "accounts.create.wallet.queue"

class RoutingKey(StrEnum):
    USER_CREATED_ROUTING_KEY = "accounts.user.created"
    ORDER_PAID_ROUTING_KEY = "orders.order.paid"
    STORE_CREATED_ROUTING_KEY = "catalogs.store.created"

ACCOUNTS_EXCHANGE = "accounts.events"
ORDERS_EXCHANGE = "orders.events"


USER_CREATED_ROUTING_KEY = "accounts.user.created"
CREATE_CART_QUEUE = "orders.create_cart.queue"

ORDER_PAID_QUEUE = 'orders.order.paid.queue'
ORDER_PAID_ROUTING_KEY = "orders.order.paid"