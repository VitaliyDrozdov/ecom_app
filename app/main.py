from fastapi import FastAPI

from app.routers import auth, category, permissions, products, reviews

app = FastAPI()
app_v1 = FastAPI(title="API v1", description="E-com first API version")
app_v2 = FastAPI(title="API v2", description="E-com second API version")


@app.get("/")
async def welcome() -> dict:
    return {"message": "e-commerce app"}


@app_v1.get("/products")
async def get_products_v21():
    return {"message": "e-commerce API v1"}


@app_v2.get("/products")
async def get_products_v2():
    return {"message": "e-commerce API v2"}


app.mount("/v1", app_v1)
app.mount("/v2", app_v2)

app.include_router(category.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(permissions.router)
app.include_router(reviews.router)
