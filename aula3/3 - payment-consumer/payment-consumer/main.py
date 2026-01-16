import asyncio

from dotenv import load_dotenv

from consumer.payment_consumer import PaymentConsumer

load_dotenv()


async def main():
    consumer = PaymentConsumer()
    await consumer.start()


if __name__ == "__main__":
    asyncio.run(main())
