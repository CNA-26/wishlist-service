from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter()

#"databas" i minnet
wishlists: Dict[str, List[str]] = {}

# Detta simulerar "Produktsregister (products API)" från din Miro-board
PRODUCT_CATALOG = {
    "P001": {"name": "Monstera", "price": 25, "image": "https://placehold.co/500x500?text=Monstera"},
    "P002": {"name": "Alocasia", "price": 59, "image": "https://placehold.co/500x500?text=Alocasia"},
    "P003": {"name": "Strelitzia", "price": 139, "image": "https://placehold.co/500x500?text=Strelitzia"}
}

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
    # 1. Hämta id-listan för användaren
    product_codes = wishlists.get(user_id, [])
    
    # 2. Skapa en lista med fullständig info från din placeholder-katalog
    detailed_products = []
    for code in product_codes:
        # Hämta info från PRODUCT_CATALOG, använd fallback om id:t saknas
        info = PRODUCT_CATALOG.get(code, {"name": "Okänd växt", "pris": 0, "image": "https://placehold.co/500x500?text=Saknas"})
        detailed_products.append({
            "productCode": code,
            **info
        })
        
    return {
        "userId": user_id,
        "products": detailed_products
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