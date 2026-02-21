from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.database import Base


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    product_code = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "product_code", name="uq_user_product"),
    )
