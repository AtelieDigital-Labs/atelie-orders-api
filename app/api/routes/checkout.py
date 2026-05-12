from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus


from app.services.shipping_service import ShippingService
from app.integrations.accounts_integration import AccountsIntegration
from app.schemas.shipping import CartShippingResponse

from fastapi import HTTPException
from typing import Annotated
from app.core.database import get_session
from app.api.dependencies import verify_user
from app.validators.validate import validate_address_user


router = APIRouter(prefix='/api/checkout', tags=['Checkout'])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/shipping/{address_id}", status_code=HTTPStatus.OK, response_model=CartShippingResponse)
async def get_shipping_options(
    address_id: str, 
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(verify_user) 
):

    address_data = await AccountsIntegration.get_address(address_id)
    
    validate_address_user(address_data, user_id)
    
    destination_zip = address_data.get('zip_code')

    options = await ShippingService.calculate_cart_shipping(
        session=session, 
        user_id=user_id, 
        destination_zip=destination_zip
    )

    return options
