from fastapi import APIRouter

order_client_router = APIRouter(prefix='/order', tags=['order'])

@order_client_router.get("/")
async def orders():
    return {'message': 'Rota Acessada'}