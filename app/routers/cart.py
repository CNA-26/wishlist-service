from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import require_jwt
from app.routers.frontendPoint import wishlists

router = APIRouter()

# Request modell för cart-API
class MoveToCartRequest(BaseModel):
    productCode: str
    quantity: int = 1


# Placeholder endpoint för cart-API
@router.post("/wishlist/{user_id}/move-to-cart")
def move_to_cart(user_id: str, data: MoveToCartRequest):
    # kontollera att produkten finns i önskelistan
    products = wishlists.get(user_id, [])
    if data.productCode not in products:
        raise HTTPException(status_code=404, detail="Produkten finns inte i önskelistan")
    
    # ta bort produkt frpn önskelistan
    products.remove(data.productCode)
    wishlists[user_id] = products

    return {
        "message": "Produkt flyttad till kundvagnen",
        "userId": user_id,
        "moved": {
            "productCode": data.productCode,
            "quantity": data.quantity
        },
        "wishlistNow": wishlists.get(user_id, [])
    }