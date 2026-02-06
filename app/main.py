from fastapi import FastAPI
from routers.frontendPoint import router as wishlist_router

app = FastAPI()

app.include_router(wishlist_router)
