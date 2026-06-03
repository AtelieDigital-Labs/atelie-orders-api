from fastapi import APIRouter, Depends
from http import HTTPStatus
from redis.asyncio import Redis
from app.core.redis import get_redis


from app.services.shipping_service import ShippingService
from app.schemas.shipping import CartShippingResponse
from app.api.dependencies.autenticator import verify_user
from app.validators.validate import validate_address_user
from app.api.dependencies.shipping import get_shipping_service
from app.api.dependencies.integration import get_accounts_integration
from app.integrations.accounts_integration import AccountsIntegration


router = APIRouter(prefix='/api/v1/checkout', tags=['Checkout'])


@router.get("/shipping/{address_id}", status_code=HTTPStatus.OK, response_model=CartShippingResponse)
async def get_shipping_options(
    address_id: str, 
    user_auth: dict = Depends(verify_user),
    service: ShippingService = Depends(get_shipping_service),
    accounts_inte: AccountsIntegration = Depends(get_accounts_integration)
):

    user_id = user_auth["user_id"]
    token = user_auth["token"]

    address_data = await accounts_inte.get_address(
        address_id=address_id, 
        token=token
    )
    
    validate_address_user(
        address=address_data,
        user_id=user_id
    )
    
    destination_zip = address_data.get('zip_code')

    options = await service.calculate_cart_shipping(
        user_id=user_id, 
        destination_zip=destination_zip
    )

    return options
