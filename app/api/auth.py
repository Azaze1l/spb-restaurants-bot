from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.config import settings
from app.db import Admins, get_db
from app.db.tokens import Tokens
from app.helpers.auth import verify_password, create_access_token, reusable_oauth2
from app.helpers.deps import get_current_user
from app.schemas.auth import Token, Auth, Admin

auth_router = APIRouter()


@auth_router.post("/login", response_model=Token)
async def login_user(data: Auth, request: Request, db=Depends(get_db)):
    admin = await Admins.get_default_admin(db=db, login=settings.DEFAULT_ADMIN_LOGIN)
    if not admin:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(data.password, admin.get("password_hash")):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    admin["id"] = str(admin.get("_id"))

    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRATION_TIME)
    access_token = create_access_token(
        subject=admin.get("id"),
        expires_delta=access_token_expires,
    )
    response = JSONResponse(
        Token(access_token=access_token, token_type="bearer").dict()
    )
    response.set_cookie(reusable_oauth2.token_name, access_token, httponly=True)
    return response


@auth_router.post("/logout")
async def logout(request: Request, user=Depends(get_current_user), db=Depends(get_db)):
    token = request.cookies.get(reusable_oauth2.token_name)
    if not token:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        token = param
    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    _ = await Tokens.add_invalidated_token(db, user_id=user.id, token=token)
    return {"status": "ok"}


@auth_router.get("/me", response_model=Admin)
async def get_current_user(user=Depends(get_current_user), db=Depends(get_db)):
    return user
