from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from schemas.order import OrderCreate, OrderRead
from typing import Annotated
from core.database import get_session
from sqlalchemy.orm import Session
from api.dependencies import verify_user

router = APIRouter(prefix='/order', tags=['order'], dependencies=[Depends(verify_user)])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/")
async def orders():
    return {'message': 'Rota Acessada'}

# Criação da ordem
@router.post('/', status_code=HTTPStatus.CREATED)
async def create(order_data: OrderCreate, session: SessionDep, user_id: str = Depends(verify_user)):
    return {'message': 'Ordem criada'}
    # return OrderService.create_new_order(session, order_data)

# Listar ordens

# Listar detalhes de uma ordem 
@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model= OrderRead)
async def list(session: SessionDep, order_id: int):
    return {'message': 'Ordem listada'}
   # return OrderService.list_order(session, order_data)