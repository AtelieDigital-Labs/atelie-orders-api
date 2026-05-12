from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from app.schemas.order import OrderArtisanRead, OrderArtisanResponse, OrderArtisanStatusUpdate
from app.services.order_service import OrderService
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import verify_user
from app.core.database import get_session

router = APIRouter(prefix='/api/stores/orders', tags=['Store orders'], dependencies=[Depends(verify_user)])

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.get('/', status_code=HTTPStatus.OK, response_model=Page[OrderArtisanResponse])
async def list_all_orders(session: SessionDep, user_id: str = Depends(verify_user)):
    """
    Lista todos os pedidos do artesão
    """
    return await OrderService.get_all_orders_artisan(session, user_id)


@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model= OrderArtisanRead)
async def list_order(session: SessionDep, order_id: int,  user_id: str = Depends(verify_user)):
   """
    Lista os detalhes de um pedido do artesão
   """
   return await OrderService.get_order_artisan_by_id(session, order_id, user_id)

@router.patch('/{oder_id}/status', status_code=HTTPStatus.OK, response_model=OrderArtisanRead)
async def update_status(session: SessionDep, order_id: int, update_status: OrderArtisanStatusUpdate, user_id: str = Depends(verify_user)):
    """
    Atualizar status de um pedido
    """
    return await OrderService.update_status_order(session, order_id, user_id, update_status)