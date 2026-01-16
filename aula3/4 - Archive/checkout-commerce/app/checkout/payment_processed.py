from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.checkout.checkout_model import Checkout
from app.checkout.checkout_request import PaymentProcessedRequest
from app.infra.database import get_db


async def payment_processed(
    request: PaymentProcessedRequest,
    db: AsyncSession = Depends(get_db),
):
    checkout = await db.get(Checkout, request.checkout_id)
    if not checkout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkout not found",
        )

    checkout.payment_id = request.payment_id
    await db.commit()
