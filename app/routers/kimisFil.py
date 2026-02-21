from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from app.auth import require_jwt

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



#Endpoints för frontend
@router.post("/wishlist")
def add_to_wishlist(data: AddToWishlistRequest, user=Depends(require_jwt)):
    if data.userId not in wishlists:
        wishlists[data.userId] = []

    wishlists[data.userId].append(data.productCode)

    return {
        "message": "Produkt tillsatt till önskelistan",
        "userId": data.userId,
        "products": wishlists[data.userId]
    }


@router.get("/wishlist/{user_id}")
def get_wishlist(user_id: str, user=Depends(require_jwt)):
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

