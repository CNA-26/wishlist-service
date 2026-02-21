from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from app.auth import require_jwt

router = APIRouter()

#"databas" i minnet
wishlists: Dict[str, List[str]] = {}

#request modell för frontend
class AddToWishlistRequest(BaseModel):
    productCode: str

#lägg till wishlist (jwt required)
@router.post("/wishlist")
def add_to_wishlist(
    data: AddToWishlistRequest,
    user=Depends(require_jwt)
):
    user_id = user["user_id"]

    if user_id not in wishlists:
        wishlists[user_id] = []

    wishlists[user_id].append(data.productCode)

    return {
        "message": "Produkt tillsatt till önskelistan!",
        "userId": user_id,
        "products": wishlists[user_id]
    }

#hämta wishlist (jwt required)
@router.get("/wishlist")
def get_wishlist(user=Depends(require_jwt)):
    user_id = user["user_id"]

    return {
        "userId": user_id,
        "products": wishlists.get(user_id, [])
    }

#ta bort från wishlist (jwt required)
@router.delete("/wishlist/{product_code}")
def remove_from_wishlist(
    product_code: str,
    user=Depends(require_jwt)
):
    user_id = user["user_id"]

    products = wishlists.get(user_id, [])

    if product_code not in products:
        raise HTTPException(status_code=404, detail="Produkten finns inte i önskelistan.")

    products.remove(product_code)
    wishlists[user_id] = products

    return {
        "message": "Produkt raderad från önskelistan.",
        "userId": user_id,
        "products": wishlists[user_id]
    }