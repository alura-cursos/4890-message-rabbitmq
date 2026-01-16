from pydantic import BaseModel


class PaymentMethod(BaseModel):
    type: str
    card_number: str
    card_expiry: str
    card_cvv: str


class PaymentRequest(BaseModel):
    checkout_id: int
    total_amount: float
    customer_email: str
    payment_method: PaymentMethod
