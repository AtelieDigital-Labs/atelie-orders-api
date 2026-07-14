from http import HTTPStatus

from fastapi_pagination import Page
from app.schemas.order import OrderCheckoutRequest, OrderCreatedResponse, OrderRead, OrderResponse, OrderPaymentRequest
from fastapi import APIRouter, Depends, Query
from app.services.order_service import OrderService
from app.api.dependencies.order import get_order_service
from app.api.dependencies.autenticator import verify_user
from app.models.order import OrderStatus

router = APIRouter(prefix='/api/v1/orders', tags=['Users order'])


@router.get('/', status_code=HTTPStatus.OK, response_model=Page[OrderResponse])
async def list_all_orders(
    status: OrderStatus | None = Query(None),
    user_auth: dict = Depends(verify_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Lista todos os pedidos do cliente
    """

    user_id = user_auth["user_id"]

    return await service.get_all_orders(user_id=user_id,status=status)


@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model= OrderRead)
async def list_order(
    order_id: int,  
    user_auth: dict = Depends(verify_user),
    service: OrderService = Depends(get_order_service)
):
   """
    Lista os detalhes de um pedido
   """
   user_id = user_auth["user_id"]
   
   return await service.get_order_by_id(order_id=order_id, user_id=user_id)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=OrderCreatedResponse)
async def create_order(
    order_data:OrderCheckoutRequest, 
    user_auth: dict = Depends(verify_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Criar um pedido
    """
    user_id = user_auth["user_id"]
    token = user_auth["token"]

    return await service.create_new_order(order_data=order_data, user_id=user_id, token=token)  

@router.post('/payments/retry', status_code=HTTPStatus.CREATED, response_model=OrderCreatedResponse)
async def paid_order(
    order_data: OrderPaymentRequest,
    user_auth: dict = Depends(verify_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Pagar pedido pendente
    """
    token = user_auth["token"]

    return await service.paid_order_pending(order_data=order_data, token=token)
