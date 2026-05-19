from http import HTTPStatus

from app.core.config import settings
from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt


async def verify_user(token: str = Header(..., description="Token de autenticação")):
    try: 
        dic = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM,])
        user_id = dic.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Token inválido',
            )
        return {
            "user_id": user_id, 
            "token": token
        }
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Token inválido',
        )
    except JWTError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Token inválido',
        )
    