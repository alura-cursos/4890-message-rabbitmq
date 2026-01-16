import httpx


class CheckoutClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def payment_processed(
        self,
        checkout_id: int,
        payment_id: str,
    ):
        payload = {
            "checkout_id": checkout_id,
            "payment_id": payment_id,
        }

        try:
            response = await self.client.post(
                "/checkout/payment_processed", json=payload
            )
            response.raise_for_status()
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}
