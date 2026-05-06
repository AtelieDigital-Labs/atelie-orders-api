from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from app.schemas.order import OrderCheckoutRequest, OrderCreatedResponse, OrderRead, OrderResponse
from app.services.order_service import OrderService
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import verify_user
from app.core.database import get_session

<<<<<<< HEAD
router = APIRouter(prefix='/orders', tags=['orders'], dependencies=[Depends(verify_user)])
=======
router = APIRouter(prefix='/api/orders', tags=['order'], dependencies=[Depends(verify_user)])
>>>>>>> 6dc8465 (feat: include webhook payment)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Criação da ordem
@router.post('/', status_code=HTTPStatus.CREATED, response_model=OrderCreatedResponse)
async def create(order_data:OrderCheckoutRequest, session: SessionDep, user_id: str = Depends(verify_user)):
     return await OrderService.create_new_order(order_data, session, user_id)  
 

@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model= OrderRead)
async def list(session: SessionDep, order_id: int,  user_id: str = Depends(verify_user)):
   """
    Lista os detalhes de um pedido
   """
   return await OrderService.get_order_by_id(session, order_id, user_id)


@router.get('/', status_code=HTTPStatus.OK, response_model=Page[OrderResponse])
async def list_orders(session: SessionDep, user_id: str = Depends(verify_user)):
    """
    Lista todos os pedidos do cliente
    """
    return await OrderService.get_all_orders(session, user_id)