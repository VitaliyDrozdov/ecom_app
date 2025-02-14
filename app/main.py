import datetime as dt

from celery import Celery
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.routers import auth, category, permissions, products, reviews
from app.tasks import call_background_task
from app.utils.log import log_middleware
from app.utils.timing import TimingMiddleware

app = FastAPI()
app_v1 = FastAPI(title="API v1", description="E-com first API version")
app_v2 = FastAPI(title="API v2", description="E-com second API version")

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
    broker_connection_retry_on_startup=True,
)


@app_v1.get("/products")
async def get_products_v1():
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

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(TimingMiddleware)

app.middleware("http")(log_middleware)


@app.get("/")
async def hello_world(message: str):
    call_background_task.apply_async(
        args=[message],
        eta=dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=1),
    )
    return {"message": "Hello World!"}
