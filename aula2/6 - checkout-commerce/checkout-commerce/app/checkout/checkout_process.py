from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.checkout.checkout_model import Checkout, CheckoutStatus
from app.checkout.checkout_request import CheckoutRequest
from app.infra.database import get_db
from app.infra.rabbitmq_producer import RabbitMQProducer, get_rabbitmq_producer


async def checkout_process(
    checkout_request: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    rabbitmq_producer: RabbitMQProducer = Depends(get_rabbitmq_producer),
):
    checkout = Checkout(
        customer_email=checkout_request.customer_email,
        total_amount=sum(item.price for item in checkout_request.items),
        status=CheckoutStatus.PENDING.value,
    )
    db.add(checkout)
    await db.commit()
    await db.refresh(checkout)

    await rabbitmq_producer.publish_payment_request(
        checkout_id=checkout.id,
        total_amount=checkout.total_amount,
        customer_email=checkout.customer_email,
        payment_method={
            "type": checkout_request.payment_method.type,
            "card_number": checkout_request.payment_method.card_number,
            "card_expiry": checkout_request.payment_method.card_expiry,
            "card_cvv": checkout_request.payment_method.card_cvv,
        },
    )

    checkout.status = CheckoutStatus.PROCESSING_PAYMENT.value
    await db.commit()

    return {"checkout_id": checkout.id, "status": checkout.status, "error": None}
