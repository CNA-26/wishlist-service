from fastapi import FastAPI
from app.routers.frontendPoint import router as wishlist_router

app = FastAPI()

app.include_router(wishlist_router)

@app.get("/")
def root():
    return {"message": "Wishlist service funkkar!"}

