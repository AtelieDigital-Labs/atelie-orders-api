from fastapi import  APIRouter, Depends
from app.api.dependencies import verify_user
from redis.asyncio import Redis
from typing import Annotated
from app.core.redis import get_redis
from http import HTTPStatus
from app.schemas.cart import CartItemRead, CartItemCreate, CartItemUpdate, CartItemReadUpdated
from app.services.cart_service import CartService



router = APIRouter(prefix='/api/v1/carts', tags=['Carts'], dependencies=[Depends(verify_user)])


RedisDep = Annotated[Redis, Depends(get_redis)]

@router.post('/items/', status_code=HTTPStatus.CREATED, response_model=CartItemRead)
async def add_to_cart(redis: RedisDep, item: CartItemCreate,user_auth: str = Depends(verify_user)):
    """Adicionar um produto ao carrinho"""

    # user_id = user_auth["user_id"]

    return await CartService.add_item(redis, item, user_auth)

@router.post('/items/{item_id}', status_code=HTTPStatus.OK, response_model=CartItemReadUpdated)
async def update_item_quantity(redis: RedisDep, item_id: int, item: CartItemUpdate,user_auth: str = Depends(verify_user)):
    """Altera a quantidade de um produto do carrinho"""

    # user_id = user_auth["user_id"]

    return await CartService.update_item_quantity(redis, item_id, item, user_auth)
