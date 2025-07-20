from fastapi import FastAPI
from .api.orders import router as orders_router
from .api.products import router as products_router
from .core.database import db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.orders.create_index("user_Id")
    await db.products.create_index([("name", "text")])
    await db.products.create_index("sizes.size")
    
    print("✅ MongoDB indexes created")
    yield
    print("🛑 Application shutdown")




app = FastAPI(lifespan=lifespan)


app.include_router(orders_router)
app.include_router(products_router)


