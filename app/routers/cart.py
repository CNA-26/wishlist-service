from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.auth import require_jwt
import httpx
from app.routers.frontendPoint import wishlists

router = APIRouter()

# Cart service enligt deras README
CART_BASE_URL = "https://cart-services-git-cartservices.2.rahtiapp.fi"

CART_API_KEY = "placeholder-key"


class MoveToCartRequest(BaseModel):
    productCode: str
    quantity: int = 1


@router.post("/wishlist/{user_id}/move-to-cart")
async def move_to_cart(
    user_id: str,
    data: MoveToCartRequest,
    claims: dict = Depends(require_jwt),
):
    # Kontrollera att JWT matchar user_id
    token_user = claims.get("sub")
    if not token_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT saknar 'sub' claim")

    if token_user != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Du får inte ändra någon annans wishlist")

    # Kontrollera att produkten finns i wishlisten
    products = wishlists.get(user_id, [])
    if data.productCode not in products:
        raise HTTPException(status_code=404, detail="Produkten finns inte i önskelistan")

    # lägg till item i cart
    cart_url = f"{CART_BASE_URL}/cart/{user_id}/add-item"
    cart_payload = {
        "product_id": data.productCode,
        "quantity": data.quantity,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                cart_url,
                json=cart_payload,
                headers={"Authorization": f"ApiKey {CART_API_KEY}"},
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Cart Service timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Kunde inte nå Cart Service: {str(e)}")


    if resp.status_code not in (200, 201):
        raise HTTPException(
            status_code=502,
            detail={"message": "Cart service error", "status": resp.status_code, "body": resp.text},
        )

    # ta bort från wishlist
    products.remove(data.productCode)
    wishlists[user_id] = products

    return {
        "message": "Produkt flyttad till kundvagnen",
        "userId": user_id,
        "moved": {"productCode": data.productCode, "quantity": data.quantity},
        "wishlistNow": products,
    }