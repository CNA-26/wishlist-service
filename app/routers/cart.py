import os
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.auth import require_jwt
from app.database import get_db
from app.models import WishlistItem

router = APIRouter()

CART_API_URL = os.getenv(
    "CART_API_URL",
    "https://cart-services-git-cartservices.2.rahtiapp.fi"
)
PRODUCTS_API_URL = os.getenv(
    "PRODUCTS_API_URL",
    "https://product-service-products-service.2.rahtiapp.fi"
)


class MoveToCartRequest(BaseModel):
    userId: str
    productCode: str


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Saknar Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Ogiltig Authorization. Expected: Bearer <token>")
    return authorization[7:].strip()


def _token_user_id(user: object) -> str | None:
    if isinstance(user, dict):
        return user.get("user_id")
    return getattr(user, "user_id", None)


def _get_product_by_code(product_code: str) -> dict:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{PRODUCTS_API_URL}/products")
            resp.raise_for_status()
            products = resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Kunde inte nå product-service: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Product-service fel ({e.response.status_code}): {e.response.text}")
    
    for p in products:
        if p.get("product_code") == product_code:
            return p
        
    raise HTTPException(status_code=404, detail="Produkten hittades inte i produktregistret")


# Flytta produkt från wishlist till cart-service
@router.post("/wishlist/move-to-cart")
def move_to_cart(
    data: MoveToCartRequest,
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
    authorization: str = Header(None, alias="Authorization")
):
    token_uid = user.get("user_id")
    if token_uid and token_uid != data.userId:
        raise HTTPException(status_code=403, detail="userId matchar inte token-användaren.")

    # Kontrollera att produkten finns i wishlisten
    item = db.query(WishlistItem).filter_by(
        user_id=data.userId,
        product_code=data.productCode
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Produkten finns inte i önskelistan.")

    # Hämta productinfo
    p = _get_product_by_code(data.productCode)

    product_id = p.get("id")
    if product_id is None:
        raise HTTPException(status_code=502, detail="Produkten saknar id")
    
    image_urls = p.get("image_urls") or []
    image_url = image_urls[0] if len(image_urls) > 0 else ""

    cart_payload = {
        "product_id": int(product_id),
        "name": p.get("product_name"),
        "price": float(p.get("price")),
        "quantity": 1,
        "image_url": image_url,
    }

    if cart_payload["name"] is None or p.get("price") is None:
        raise HTTPException(status_code=502, detail="Produktregistret saknar product_name eller price")
    
    try:
        token = _extract_bearer_token(authorization)

        with httpx.Client(timeout=5.0) as client:
            resp = client.post(
                f"{CART_API_URL}/cart/{data.userId}/add-item",
                json=cart_payload,
                headers={"Authorization": f"Bearer {token}"}
            )
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Kunde inte nå cart-service: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"cart-service fel ({e.response.status_code}): {e.response.text}")

    # ta bort från wishlist
    db.delete(item)
    db.commit()

    remaining = [
        i.product_code
        for i in db.query(WishlistItem).filter_by(user_id=data.userId).all()
    ]

    return {
        "message": "Produkten flyttades till varukorgen och togs bort från önskelistan.",
        "userId": data.userId,
        "productCode": data.productCode,
        "remainingWishlist": remaining,
    }