from enum import StrEnum

class Exchange(StrEnum):
    ACCOUNTS_EXCHANGE = "accounts.events"
    ORDER_EXCHANGE = "orders.events"
    CATALOG_EXCHANGE = "catalogs.events"
    DQL_EXCHANGE = "dql.evenvts"
    LOG_EXCHANGE = "logs.events"

class Queue(StrEnum):
    USER_CREATED_QUEUE = "accounts.user.created.queue"
    WALLET_TRANSACTION_QUEUE = 'accounts.wallet.transaction.queue'
    BECOME_ARTISAN_QUEUE= "accounts.become.artisan.queue"
    CREATE_WALLET_QUEUE= "accounts.create.wallet.queue"
    ORDER_EXPIRED_QUEUE = "orders.order.expired.queue"
    LOG_REGISTER_QUEUE = "logs.register.queue" # verificar se ele precisa saber 

class RoutingKey(StrEnum):
    USER_CREATED_ROUTING_KEY = "accounts.user.created"
    ORDER_PAID_ROUTING_KEY = "orders.order.paid"
    ORDER_CREATED_ROUTING_KEY = "orders.order.created"
    STORE_CREATED_ROUTING_KEY = "catalogs.store.created"
    STOCK_RESERVATION_EXPIRE_ROUTING_KEY = "catalogs.stock.reservation.expire"
    LOG_REGISTER_ROUTING_KEY = "logs.register"