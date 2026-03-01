import os
from fastapi import Header, HTTPException
from jose import JWTError, jwt

JWT_SECRET = os.getenv("JWT_SECRET")

def require_jwt(authorization: str = Header(None, alias="Authorization")):
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="JWT_SECRET is not configured")
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth")
    
    token = authorization[7:].strip()

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False, "verify_iss": False},
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing 'sub' claim")
        
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

