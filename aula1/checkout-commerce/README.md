# checkout-commerce

A commerce checkout application built with FastAPI that orchestrates the checkout process by integrating with payment, inventory, and order services.

## Overview

This application provides a checkout API that processes e-commerce orders by:

1. **Creating a checkout record** in the PostgreSQL database
2. **Processing payment** through the payment service
3. **Deducting inventory** through the inventory service
4. **Creating an order** through the order service

If any step fails, the checkout is marked as failed and an appropriate error is returned.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│   Client        │────▶│  Checkout API    │
└─────────────────┘     │  (FastAPI)       │
                        └────────┬─────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐    ┌───────────────────┐    ┌───────────────┐
│ Payment       │    │ Inventory         │    │ Order         │
│ Service       │    │ Service           │    │ Service       │
│ (Port 8081)   │    │ (Port 8082)       │    │ (Port 8083)   │
└───────────────┘    └───────────────────┘    └───────────────┘

```

## Tech Stack

- **Python 3.13+**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM with async support
- **PostgreSQL** - Database
- **httpx** - Async HTTP client
- **uv** - Package manager
- **WireMock** - Mock services for development

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Docker and Docker Compose

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/StephanyBatista/checkout-commerce.git
cd checkout-commerce
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Start the infrastructure services

Start PostgreSQL and mock services (payment, inventory, order) using Docker Compose:

```bash
docker-compose up -d
```

This will start:

- **PostgreSQL** on port `5442`
- **Payment Service Mock** on port `8081`
- **Inventory Service Mock** on port `8082`
- **Order Service Mock** on port `8083`

### 4. Set up environment variables

Create a `.env` file in the project root with the following variables:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5442/checkout_db
PAYMENT_SERVICE_URL=http://localhost:8081
INVENTORY_SERVICE_URL=http://localhost:8082
ORDER_SERVICE_URL=http://localhost:8083
APP_HOST=0.0.0.0
APP_PORT=8005
```

### 5. Run the application

```bash
chmod +x run-dev.sh
./run-dev.sh
```

Or run directly with uv:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

The API will be available at `http://localhost:8005`.

## API Endpoints

### Health Check

```http
GET /health
```

### Process Checkout

```http
POST /checkout/process
Content-Type: application/json

{
  "payment_method": {
    "type": "credit_card",
    "card_number": "4111111111111111",
    "card_expiry": "12/25",
    "card_cvv": "123"
  },
  "customer_email": "customer@example.com",
  "shipping_address": {
    "street": "Rua das Flores",
    "number": "123",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01234-567"
  },
  "items": [
    {
      "product_id": "prod_001",
      "quantity": 2,
      "price": 99.90
    },
    {
      "product_id": "prod_002",
      "quantity": 1,
      "price": 149.90
    }
  ]
}
```

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc

## Project Structure

```
checkout-commerce/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── client_manager.py    # HTTP client lifecycle management
│   ├── checkout/
│   │   ├── __init__.py
│   │   ├── checkout_model.py    # Database model
│   │   ├── checkout_process.py  # Checkout business logic
│   │   ├── checkout_request.py  # Request DTOs
│   │   └── router.py            # API routes
│   └── infra/
│       ├── database.py          # Database configuration
│       └── client/
│           ├── inventory_client.py
│           ├── order_client.py
│           └── payment_client.py
├── wiremock/                # Mock service configurations
├── docker-compose.yml
├── pyproject.toml
├── run-dev.sh
└── README.md
```

## Development

### Running tests

```bash
uv run pytest
```

### Stopping services

```bash
docker-compose down
```

### Viewing logs

```bash
docker-compose logs -f
```
