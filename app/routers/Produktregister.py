import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from app.auth import require_jwt
from app.database import get_db
from app.models import WishlistItem

router = APIRouter()

PRODUCTS_API_URL = os.getenv(
    "PRODUCTS_API_URL",
    "https://product-service-products-service.2.rahtiapp.fi"
)


class AddToWishlistRequest(BaseModel):
    userId: str
    productCode: str


def fetch_products_by_codes(product_codes: list[str]) -> list[dict]:
    """Hämta produktinfo från Produktregister (products API) för givna koder."""
    if not product_codes:
        return []

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{PRODUCTS_API_URL}/products")
            resp.raise_for_status()
            all_products = resp.json()
    except httpx.RequestError:
        # Om Produktregister inte svarar, returnera koder utan info
        return [
            {"productCode": code, "product_name": "Okänd produkt", "price": None, "img": None}
            for code in product_codes
        ]

    # Bygg en lookup-dict med product_code som nyckel
    catalog = {p["product_code"]: p for p in all_products}

    result = []
    for code in product_codes:
        info = catalog.get(code)
        if info:
            result.append({
                "productCode": code,
                "product_name": info["product_name"],
                "price": info["price"],
                "img": info["img"],
                "description": info.get("description_text"),
            })
        else:
            result.append({
                "productCode": code,
                "product_name": "Okänd produkt",
                "price": None,
                "img": None,
            })

    return result


# Lägg till produkt i wishlist (JWT krävs)
@router.post("/wishlist")
def add_to_wishlist(
    data: AddToWishlistRequest,
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
):
    existing = db.query(WishlistItem).filter_by(
        user_id=data.userId, product_code=data.productCode
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Produkten finns redan i önskelistan.")

    db.add(WishlistItem(user_id=data.userId, product_code=data.productCode))
    db.commit()

    all_codes = [
        i.product_code
        for i in db.query(WishlistItem).filter_by(user_id=data.userId).all()
    ]
    return {
        "message": "Produkt tillsatt till önskelistan",
        "userId": data.userId,
        "products": all_codes,
    }


# Hämta wishlist med fullständig produktinfo (JWT krävs)
@router.get("/wishlist/{user_id}")
def get_wishlist(
    user_id: str,
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
):
    items = db.query(WishlistItem).filter_by(user_id=user_id).all()
    product_codes = [item.product_code for item in items]

    return {
        "userId": user_id,
        "products": fetch_products_by_codes(product_codes),
    }


# Ta bort produkt från wishlist (JWT krävs)
@router.delete("/wishlist/{user_id}/{product_code}")
def remove_from_wishlist(
    user_id: str,
    product_code: str,
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
):
    item = db.query(WishlistItem).filter_by(
        user_id=user_id, product_code=product_code
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Produkten finns inte i önskelistan.")

    db.delete(item)
    db.commit()

    remaining = [
        i.product_code
        for i in db.query(WishlistItem).filter_by(user_id=user_id).all()
    ]
    return {
        "message": "Produkt raderad från önskelistan.",
        "userId": user_id,
        "products": remaining,
    }
