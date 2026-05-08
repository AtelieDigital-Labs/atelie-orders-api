from http import HTTPStatus

from app.core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

# Quando tiver a conexão com a API atualizar a rota
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token-mock")

async def verify_user(token: str = Depends(oauth2_scheme)):
    try: 
        dic = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        user_id = dic.get("sub")
        
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
    