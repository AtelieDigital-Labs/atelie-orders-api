from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from app.schemas.order import OrderCreate, OrderCreatedResponse, OrderRead
from app.services.order_service import OrderService
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import verify_user
from app.core.database import get_session

router = APIRouter(prefix='/order', tags=['order'], dependencies=[Depends(verify_user)])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/")
async def orders():
    return {'message': 'Rota Acessada'}

# Criação da ordem
@router.post('/', status_code=HTTPStatus.CREATED, response_model=OrderCreatedResponse)
async def create(order_data: OrderCreate, session: SessionDep, user_id: str = Depends(verify_user)):
     return await OrderService.create_new_order(session, order_data, user_id)  
 
# Listar ordens
# Criar função

# Listar detalhes de uma ordem 
@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model= OrderRead)
async def list(session: SessionDep, order_id: int):
    return {'message': 'Ordem listada'}
   # return OrderService.list_order(session, order_data)