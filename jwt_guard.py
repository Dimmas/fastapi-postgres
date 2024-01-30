from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from jwt_service import decode_token
from user_service import create_user

security = HTTPBearer()


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    uid = payload.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="UID IS ABSEND")

    user = await create_user(uid=uid)
    if not user:
        raise HTTPException(status_code=500, detail="USER_NOT_FOUND")

    return user
