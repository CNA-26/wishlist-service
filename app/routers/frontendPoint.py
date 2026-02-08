from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter()

#"databas" i minnet
wishlists: Dict[str, List[str]] = {}

#Request modell för frontend
class AddToWishlistRequest(BaseModel):
    userId: str
    productCode: str

# Request modell för cart-API
class MoveToCartRequest(BaseModel):
    productCode: str
    quantity: int = 1



#Endpoints för frontend
@router.post("/wishlist")
def add_to_wishlist(data: AddToWishlistRequest):
    if data.userId not in wishlists:
        wishlists[data.userId] = []

    wishlists[data.userId].append(data.productCode)

    return {
        "message": "Produkt tillsatt till önskelistan",
        "userId": data.userId,
        "products": wishlists[data.userId]
    }


@router.get("/wishlist/{user_id}")
def get_wishlist(user_id: str):
    return {
        "userId": user_id,
        "products": wishlists.get(user_id, [])
    }


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