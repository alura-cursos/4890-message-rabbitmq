import json
import os

import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
EXCHANGE_NAME = "checkout.exchange"
QUEUE_NAME = "payment.request"


class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, durable=True
            )
            queue = await self.channel.declare_queue(QUEUE_NAME, durable=True)
            await queue.bind(self.exchange, routing_key=QUEUE_NAME)

    async def publish_payment_request(
        self,
        checkout_id: int,
        total_amount: float,
        customer_email: str,
        payment_method: dict,
    ):
        await self.connect()

        message_body = {
            "checkout_id": checkout_id,
            "total_amount": total_amount,
            "customer_email": customer_email,
            "payment_method": payment_method,
        }

        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=QUEUE_NAME,
        )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


rabbitmq_producer = RabbitMQProducer()


def get_rabbitmq_producer() -> RabbitMQProducer:
    return rabbitmq_producer
