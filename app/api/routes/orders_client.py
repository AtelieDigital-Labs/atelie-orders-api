from http import HTTPStatus
from typing import Annotated

from fastapi_pagination import Page
from app.schemas.order import OrderCheckoutRequest, OrderCreatedResponse, OrderRead, OrderResponse
from fastapi import APIRouter, Depends, Request, HTTPException
from app.services.order_service import OrderService
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import verify_user
from app.core.database import get_session

router = APIRouter(prefix='/api/v1/orders', tags=['Users order'], dependencies=[Depends(verify_user)])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
 

@router.get('/', status_code=HTTPStatus.OK, response_model=Page[OrderResponse])
async def list_all_orders(session: SessionDep, user_id: str = Depends(verify_user)):
    """
    Lista todos os pedidos do cliente
    """
    return await OrderService.get_all_orders(session, user_id)


@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model= OrderRead)
async def list_order(session: SessionDep, order_id: int,  user_id: str = Depends(verify_user)):
   """
    Lista os detalhes de um pedido
   """
   return await OrderService.get_order_by_id(session, order_id, user_id)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=OrderCreatedResponse)
async def create_order(order_data:OrderCheckoutRequest, session: SessionDep, user_auth: dict = Depends(verify_user)):
    """
    Criar um pedido
    """
    user_id = user_auth["user_id"]
    token = user_auth["token"]

    return await OrderService.create_new_order(order_data, session, user_id, token)  