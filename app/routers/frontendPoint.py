from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter()

#"databas" i minnet
wishlists: Dict[str, List[str]] = {}

#Request modell för frontend
class AddToWishlistRequest(BaseModel):
    userId: str
    productCode: str



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
