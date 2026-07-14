from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from app.schemas.order import OrderArtisanRead, OrderArtisanResponse, OrderArtisanStatusUpdate
from app.services.order_service import OrderService
from app.api.dependencies.order import get_order_service
from app.api.dependencies.autenticator import verify_user

router = APIRouter(prefix='/api/v1/stores/orders', tags=['Store orders'], dependencies=[Depends(verify_user)])
 

@router.get('/', status_code=HTTPStatus.OK, response_model=Page[OrderArtisanResponse])
async def list_all_orders(
    user_auth: dict = Depends(verify_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Lista todos os pedidos do artesão
    """
    token = user_auth["token"]

    return await service.get_all_orders_artisan(token=token)


@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model= OrderArtisanRead)
async def list_order(
    order_id: int,  user_auth: dict = Depends(verify_user),
    service: OrderService = Depends(get_order_service)
):
   """
    Lista os detalhes de um pedido do artesão
   """
   token = user_auth["token"]

   return await service.get_order_artisan_by_id(order_id=order_id, token=token)

@router.patch('/{order_id}/status', status_code=HTTPStatus.OK, response_model=OrderArtisanRead)
async def update_status(
    order_id: int, 
    update_status: OrderArtisanStatusUpdate, 
    user_auth: dict = Depends(verify_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Atualizar status de um pedido
    """

    token = user_auth["token"]
    
    return await service.update_status_order(order_id=order_id, token=token, update_status=update_status)