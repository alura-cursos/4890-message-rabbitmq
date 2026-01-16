import asyncio
import json
import os

import aio_pika
import httpx

from consumer.model import PaymentRequest
from consumer.payment_client import PaymentClient


class PaymentConsumer:
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.payment_service_url = os.getenv("PAYMENT_SERVICE_URL")
        self.exchange_name = "checkout.exchange"
        self.queue_name = "payment.request"
        self.client = PaymentClient(
            httpx.AsyncClient(base_url=self.payment_service_url)
        )

    async def process_message(self, message: aio_pika.IncomingMessage):
        try:
            body = json.loads(message.body)
            print(f"Received message: {body}")
            payment_request = PaymentRequest(**body)
            print(f"payment_request: {body}")
            result = await self.client.process(
                total_amount=payment_request.total_amount,
                payment_method=payment_request.payment_method,
                customer_email=payment_request.customer_email,
            )
            if result["error"]:
                print(f"Payment failed: {result['error']}")
                await message.nack(requeue=True)
            else:
                print(f"Payment succeeded, transaction ID: {result['transaction_id']}")
                await message.ack()
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            await message.nack(requeue=True)

    async def start(self):
        connection = await aio_pika.connect_robust(self.rabbitmq_url)

        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            queue = await channel.declare_queue(self.queue_name, durable=True)
            await queue.bind(exchange, routing_key=self.queue_name)
            await queue.consume(self.process_message)
            print("PaymentConsumer is listening for messages...")

            await asyncio.Future()  # Run forever
