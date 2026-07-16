from fastapi import HTTPException
from http import HTTPStatus


def validate_address_user(address_data: dict[str, any], user_id: str):
    if not address_data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Não foi possível localizar o endereço de entrega')

    if str(address_data.get("user")) != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,detail='O endereço de entrega não pertece a este usuário')
