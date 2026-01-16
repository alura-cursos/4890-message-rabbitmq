import asyncio
import json
import os

import aio_pika
import httpx

from consumer.model import PaymentRequest
from consumer.payment_client import PaymentClient

MAX_RETRIES = 10


class PaymentConsumer:
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.payment_service_url = os.getenv("PAYMENT_SERVICE_URL")
        self.exchange_name = "checkout.exchange"
        self.dl_exchange_name = "checkout.exchange.dl"
        self.queue_name = "payment.request"
        self.dl_queue_name = "payment.request.dl"
        self.client = PaymentClient(
            httpx.AsyncClient(base_url=self.payment_service_url)
        )

    def _get_retry_count(self, message: aio_pika.IncomingMessage) -> int:
        """Get retry count from custom x-retry-count header."""
        if not message.headers:
            return 0
        return message.headers.get("x-retry-count", 0)

    async def _republish_with_retry(
        self, message: aio_pika.IncomingMessage, retry_count: int
    ):
        """Republish message with incremented retry count."""
        new_headers = dict(message.headers or {})
        new_headers["x-retry-count"] = retry_count

        new_message = aio_pika.Message(
            body=message.body,
            headers=new_headers,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.exchange.publish(new_message, routing_key=self.queue_name)

    async def process_message(self, message: aio_pika.IncomingMessage):
        retry_count = self._get_retry_count(message)
        try:
            body = json.loads(message.body)
            print(f"Received message retry {retry_count}: {body}")
            payment_request = PaymentRequest(**body)
            result = await self.client.process(
                total_amount=payment_request.total_amount,
                payment_method=payment_request.payment_method,
                customer_email=payment_request.customer_email,
            )
            if result["error"]:
                print(f"Payment failed: {result['error']}")
                if retry_count >= MAX_RETRIES:
                    print("Max retries reached, sending to dead-letter queue")
                    await message.nack(requeue=False)
                else:
                    await self._republish_with_retry(message, retry_count + 1)
                    await message.ack()
            else:
                print(f"Payment succeeded, transaction ID: {result['transaction_id']}")
                await message.ack()
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            if retry_count >= MAX_RETRIES:
                print("Max retries reached, sending to dead-letter queue")
                await message.nack(requeue=False)
            else:
                await self._republish_with_retry(message, retry_count + 1)
                await message.ack()

    async def start(self):
        connection = await aio_pika.connect_robust(self.rabbitmq_url)

        async with connection:
            channel = await connection.channel()
            self.exchange = await channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            dl_exchange = await channel.declare_exchange(
                self.dl_exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            dl_queue = await channel.declare_queue(self.dl_queue_name, durable=True)
            await dl_queue.bind(dl_exchange, routing_key=self.dl_queue_name)

            queue = await channel.declare_queue(
                self.queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": self.dl_exchange_name,
                    "x-dead-letter-routing-key": self.dl_queue_name,
                },
            )
            await queue.bind(self.exchange, routing_key=self.queue_name)
            await queue.consume(self.process_message)
            print("PaymentConsumer is listening for messages...")

            await asyncio.Future()  # Run forever
