import os
from fastapi import Header, HTTPException

JWT_SECRET = os.getenv("JWT_SECRET")

def require_jwt(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        if token != JWT_SECRET:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return {"user_id": "testuser"}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")