import os
from fastapi import APIRouter, Depends, HTTPException
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
PLACEHOLDER_API_KEY = os.getenv("PLACEHOLDER_API_KEY")


class MoveToCartRequest(BaseModel):
    userId: str
    productCode: str


def _token_user_id(user: object) -> str | None:
    if isinstance(user, dict):
        return user.get("sub") or user.get("user_id") or user.get("userId")
    return getattr(user, "sub", None) or getattr(user, "user_id", None) or getattr(user, "userId", None)


def add_item_to_cart_api(user_id: str, product_code: str) -> None:
    # Anropa cart-service för att lägga till en produkt i cart
    if not PLACEHOLDER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="PLACEHOLDER_API_KEY saknas"
        )

    headers = {"Authorization": f"ApiKey {PLACEHOLDER_API_KEY}"}
    payload = {"product_id": product_code}

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(f"{CART_API_URL}/cart/{user_id}/add-item", json=payload, headers=headers)
            resp.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Kunde inte nå cart-service: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"cart-service fel ({e.response.status_code}): {e.response.text}"
        )


# Flytta produkt från wishlist till cart-service
@router.post("/wishlist/move-to-cart")
def move_to_cart(
    data: MoveToCartRequest,
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
):
    token_uid = _token_user_id(user)
    if token_uid and token_uid != data.userId:
        raise HTTPException(status_code=403, detail="userId matchar inte token-användaren.")

    # Kontrollera att produkten finns i wishlisten
    item = db.query(WishlistItem).filter_by(
        user_id=data.userId,
        product_code=data.productCode
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Produkten finns inte i önskelistan.")

    # Lägg till i cart via cart-API
    add_item_to_cart_api(data.userId, data.productCode)

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