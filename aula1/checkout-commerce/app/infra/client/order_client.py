import os

import httpx

from app.checkout.checkout_request import ItemRequest, ShippingAddressRequest


class OrderClient:
    def __init__(self):
        self.order_service_url = os.getenv("ORDER_SERVICE_URL")
        self.client = httpx.AsyncClient(base_url=self.order_service_url)

    async def create(
        self,
        checkout_id: str,
        customer_email: str,
        shipping_address: ShippingAddressRequest,
        items: list[ItemRequest],
    ):
        payload = {
            "checkout_id": checkout_id,
            "customer_email": customer_email,
            "shipping_address": {
                "street": shipping_address.street,
                "number": shipping_address.number,
                "city": shipping_address.city,
                "state": shipping_address.state,
                "zip_code": shipping_address.zip_code,
            },
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                }
                for item in items
            ],
        }
        response = await self.client.post("/orders", json=payload)
        response.raise_for_status()
        transaction_id = response.json().get("orderId")
        return {"order_id": transaction_id, "error": None}


def get_order_client() -> OrderClient:
    return OrderClient()
