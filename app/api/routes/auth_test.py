from datetime import datetime, timedelta, timezone

from app.core.config import settings
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

router = APIRouter(tags=["Mock - Temporário"])

@router.post("/api/token-mock")
async def gerar_token_falso(form_data: OAuth2PasswordRequestForm = Depends()):

    fake_user_id = "usr_98765_teste"

    date_exp = datetime.now(timezone.utc) + timedelta(minutes=60)

    dic = {"sub": str(fake_user_id), "exp": date_exp}

    token = jwt.encode(
        dic, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return {
        "access_token": token, 
        "token_type": "bearer"
    }


# DELETAR ARQUIVO APÓS CONEXÃO COM A API ACCOUNTS