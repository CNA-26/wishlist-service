from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_jwt
from app.database import get_db
from app.models import WishlistItem
from app.routers.Produktregister import fetch_products_by_codes

router = APIRouter()


class AddToWishlistRequest(BaseModel):
    productCode: str


@router.post("/wishlist")
def add_to_wishlist(
    data: AddToWishlistRequest,
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
):
    user_id = user["user_id"]

    existing = db.query(WishlistItem).filter_by(
        user_id=user_id, product_code=data.productCode
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Produkten finns redan i önskelistan.")

    db.add(WishlistItem(user_id=user_id, product_code=data.productCode))
    db.commit()

    all_codes = [
        i.product_code
        for i in db.query(WishlistItem).filter_by(user_id=user_id).all()
    ]
    return {
        "message": "Produkt tillsatt till önskelistan!",
        "userId": user_id,
        "products": all_codes,
    }


@router.get("/wishlist")
def get_wishlist(
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
):
    user_id = user["user_id"]
    items = db.query(WishlistItem).filter_by(user_id=user_id).all()
    product_codes = [item.product_code for item in items]

    return {
        "userId": user_id,
        "products": fetch_products_by_codes(product_codes),
    }


@router.get("/wishlist/stats")
def get_wishlist_stats(db: Session = Depends(get_db)):
    rows = (
        db.query(WishlistItem.product_code, func.count(WishlistItem.user_id))
        .group_by(WishlistItem.product_code)
        .all()
    )
    return {code: count for code, count in rows}


@router.delete("/wishlist/{product_code}")
def remove_from_wishlist(
    product_code: str,
    user=Depends(require_jwt),
    db: Session = Depends(get_db),
):
    user_id = user["user_id"]

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
