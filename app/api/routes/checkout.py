from fastapi import APIRouter, Depends
from http import HTTPStatus
from redis.asyncio import Redis
from app.core.redis import get_redis



from app.services.shipping_service import ShippingService
from app.integrations.accounts_integration import AccountsIntegration
from app.schemas.shipping import CartShippingResponse

from typing import Annotated
from app.api.dependencies import verify_user
from app.validators.validate import validate_address_user


router = APIRouter(prefix='/api/v1/checkout', tags=['Checkout'])


RedisDep = Annotated[Redis, Depends(get_redis)]



@router.get("/shipping/{address_id}", status_code=HTTPStatus.OK, response_model=CartShippingResponse)
async def get_shipping_options(
    address_id: str, 
    redis: RedisDep,
    user_id: str = Depends(verify_user) 
):

    address_data = await AccountsIntegration.get_address(address_id)
    
    validate_address_user(address_data, user_id)
    
    destination_zip = address_data.get('zip_code')

    options = await ShippingService.calculate_cart_shipping(
        redis=redis, 
        user_id=user_id, 
        destination_zip=destination_zip
    )

    return options
