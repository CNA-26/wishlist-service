from fastapi import FastAPI
from app.routers.frontendPoint import router as wishlist_router
from app.routers.cart import router as cart_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wishlist_router)
app.include_router(cart_router)

@app.get("/")
def root():
    return {"message": "Wishlist service funkkar!"}

