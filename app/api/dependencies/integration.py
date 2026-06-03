from app.integrations.catalog_integration import CatalogIntegration
from app.integrations.shipping_integration import ShippingIntegration
from app.integrations.accounts_integration import AccountsIntegration
from app.integrations.payment_integration import PaymentIntegration
from app.core.config import settings


def get_catalog_integration() -> CatalogIntegration:
    return CatalogIntegration()

def get_shipping_integration() -> ShippingIntegration:
    return ShippingIntegration(token=settings.MELHOR_ENVIO_TOKEN)

def get_accounts_integration() -> AccountsIntegration:
    return AccountsIntegration()

def get_payment_integration() -> PaymentIntegration:
    return PaymentIntegration(token=settings.MERCADO_PAGO_TOKEN)