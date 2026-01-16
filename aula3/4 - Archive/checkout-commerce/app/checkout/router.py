from fastapi import APIRouter

from app.checkout.checkout_process import checkout_process
from app.checkout.payment_processed import payment_processed

router = APIRouter(prefix="/checkout", tags=["Checkout"])

router.add_api_route(
    "/process",
    endpoint=checkout_process,
    methods=["POST"],
)

router.add_api_route(
    "/payment_processed",
    endpoint=payment_processed,
    methods=["POST"],
)
