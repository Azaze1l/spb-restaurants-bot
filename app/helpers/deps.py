from fastapi import Depends, HTTPException
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.status import HTTP_403_FORBIDDEN

from app.config import settings
from app.db import Admins, get_db
from app.db.tokens import Tokens
from app.helpers.auth import reusable_oauth2, ALGORITHM
from app.schemas.auth import Admin


async def get_current_user(
    db: AsyncIOMotorDatabase = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> Admin:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    admin = await Admins.get_admin_by_id(db, admin_id=payload["sub"])
    admin["id"] = str(admin.get("_id"))
    if not admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User not found")
    token_is_invalid = await Tokens.check_user_token(db, token=token, user_id=admin["id"])
    if token_is_invalid:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return Admin(**admin)
