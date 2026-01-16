from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.checkout.checkout_model import Checkout, CheckoutStatus
from app.checkout.checkout_request import CheckoutRequest
from app.infra.client.inventory_client import InventoryClient, get_inventory_client
from app.infra.client.order_client import OrderClient, get_order_client
from app.infra.client.payment_client import PaymentClient, get_payment_client
from app.infra.database import get_db


async def checkout_process(
    checkout_request: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    payment_client: PaymentClient = Depends(get_payment_client),
    inventory_client: InventoryClient = Depends(get_inventory_client),
    order_client: OrderClient = Depends(get_order_client),
):
    checkout = Checkout(
        customer_email=checkout_request.customer_email,
        total_amount=sum(item.price for item in checkout_request.items),
        status=CheckoutStatus.PENDING.value,
    )
    db.add(checkout)
    await db.commit()
    await db.refresh(checkout)

    payment_response = await payment_client.process(
        total_amount=checkout.total_amount,
        payment_method=checkout_request.payment_method,
        customer_email=checkout_request.customer_email,
    )
    if payment_response["error"]:
        checkout.status = CheckoutStatus.FAILED.value
        checkout.error = payment_response["error"]
        await db.commit()
        raise HTTPException(
            status_code=422,
            detail={
                "checkout_id": checkout.id,
                "error": "Payment processing failed",
                "message": payment_response["error"],
            },
        )

    checkout.payment_id = payment_response["transaction_id"]

    inventory_response = await inventory_client.deduct(
        items=checkout_request.items,
    )
    if inventory_response["error"]:
        checkout.status = CheckoutStatus.FAILED.value
        checkout.error = inventory_response["error"]
        await db.commit()
        raise HTTPException(
            status_code=422,
            detail={
                "checkout_id": checkout.id,
                "error": "Inventory failed",
                "message": inventory_response["error"],
            },
        )

    order_response = await order_client.create(
        checkout_id=checkout.id,
        customer_email=checkout_request.customer_email,
        shipping_address=checkout_request.shipping_address,
        items=checkout_request.items,
    )
    if order_response["error"]:
        checkout.status = CheckoutStatus.FAILED.value
        checkout.error = order_response["error"]
        await db.commit()
        raise HTTPException(
            status_code=422,
            detail={
                "checkout_id": checkout.id,
                "error": "Order failed",
                "message": order_response["error"],
            },
        )

    checkout.order_id = order_response["order_id"]
    checkout.status = CheckoutStatus.SUCCESS.value
    await db.commit()
    return {"checkout_id": checkout.id, "error": None}
