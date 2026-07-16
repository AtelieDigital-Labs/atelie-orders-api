from fastapi import  APIRouter, Depends
from app.api.dependencies.autenticator import verify_user
from http import HTTPStatus
from app.schemas.cart import CartItemRead, CartItemCreate, CartItemUpdate, CartItemReadUpdated, CartResponse
from app.services.cart_service import CartService
from app.api.dependencies.cart import get_cart_service


router = APIRouter(prefix='/api/v1/carts', tags=['Carts'], dependencies=[Depends(verify_user)])


@router.get('/', status_code=HTTPStatus.OK, response_model=CartResponse)
async def get_cart(
    user_auth: dict = Depends(verify_user), 
    service: CartService = Depends(get_cart_service)
):
    """Listar os itens do carrinho"""

    user_id = user_auth["user_id"]

    return await service.get_items(user_id)

@router.post('/items/', status_code=HTTPStatus.CREATED, response_model=CartItemRead)
async def add_to_cart(
    item: CartItemCreate, 
    user_auth: dict = Depends(verify_user), 
    service: CartService = Depends(get_cart_service)
):
    """Adicionar um produto ao carrinho"""

    user_id = user_auth["user_id"]

    return await service.add_item(item, user_id)

@router.patch('/items/{item_id}', status_code=HTTPStatus.OK, response_model=CartItemReadUpdated)
async def update_item_quantity(
    item_id: str, 
    item: CartItemUpdate, 
    user_auth: str = Depends(verify_user), 
    service: CartService = Depends(get_cart_service)
):
    """Altera a quantidade de um produto do carrinho"""

    user_id = user_auth["user_id"]

    return await service.update_item_quantity(item_id, item, user_id)

@router.delete('/items/{item_id}', status_code=HTTPStatus.OK)
async def clear_cart_item(
    item_id: str, 
    user_auth: dict = Depends(verify_user), 
    service: CartService = Depends(get_cart_service)
):
    """Remove um item do carrinho"""

    user_id = user_auth["user_id"]

    return await service.clear_cart_item(item_id, user_id)

@router.delete('/', status_code=HTTPStatus.OK)
async def clear_cart(
    user_auth: dict = Depends(verify_user), 
    service: CartService = Depends(get_cart_service)
):
    """Limpa os dados do carrinho"""

    user_id = user_auth["user_id"]

    return await service.clear_cart(user_id)