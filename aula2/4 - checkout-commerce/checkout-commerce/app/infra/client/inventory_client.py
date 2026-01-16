import os

import httpx

from app.checkout.checkout_request import ItemRequest


class InventoryClient:
    def __init__(self):
        self.inventory_service_url = os.getenv("INVENTORY_SERVICE_URL")
        self.client = httpx.AsyncClient(base_url=self.inventory_service_url)

    async def deduct(
        self,
        items: list[ItemRequest],
    ):
        payload = {
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                }
                for item in items
            ],
        }
        response = await self.client.post("/inventory/deduct", json=payload)
        response.raise_for_status()
        return {"success": True, "error": None}


def get_inventory_client() -> InventoryClient:
    return InventoryClient()
