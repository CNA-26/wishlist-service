from fastapi import FastAPI, Depends
from app.routers.frontendPoint import router as wishlist_router
from app.routers.cart import router as cart_router
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, get_db
from app import models
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI()

# Skapa tabeller i databasen om de inte finns
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wishlist_router)
app.include_router(cart_router)

@app.get("/")
def root():
    return {"message": "Wishlist service funkkar!"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Databasen är ansluten!"}
    except Exception:
        return {"message": "Databasen är INTE ansluten!"}
    