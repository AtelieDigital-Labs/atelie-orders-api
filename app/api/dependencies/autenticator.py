from http import HTTPStatus

from app.core.config import settings
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError, jwt
from app.core.context import current_user_id

security = HTTPBearer()

async def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials
    
    try: 
        dic = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM,])
        user_id = dic.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Token inválido',
            )
        
        current_user_id.set(user_id)
        
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
    