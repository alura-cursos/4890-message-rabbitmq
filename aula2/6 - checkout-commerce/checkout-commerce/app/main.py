import os

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from app.checkout.router import router as checkout_router
from app.client_manager import client_manager
from app.infra.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup: Create database tables
    await create_tables()
    await client_manager.startup()
    yield
    await client_manager.shutdown()


app = FastAPI(title="Checkout Commerce", version="0.1.0", lifespan=lifespan)

app.include_router(checkout_router)


@app.get("/health")
async def health_check():
    payment_url = os.getenv("PAYMENT_SERVICE_URL")
    return {"status": payment_url}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8005))
    uvicorn.run(app, host=host, port=port)
