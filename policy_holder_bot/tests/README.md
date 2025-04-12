# Policy Holder Bot Tests

This directory contains unit tests for the Policy Holder Bot.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
.\venv\Scripts\activate  # On Windows
```

2. Install test dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

To run all tests:
```bash
pytest
```

To run tests with coverage report:
```bash
pytest --cov=bot
```

To generate HTML coverage report:
```bash
pytest --cov=bot --cov-report=html
```

## Test Structure

- `conftest.py` - Contains common fixtures used across tests
- `handlers/` - Tests for bot command handlers
- `clients/` - Tests for external service clients

## Test Coverage

The tests are designed to achieve at least 85% code coverage. All external dependencies (database, ICP, Open Banking API, Mailgun) are mocked to ensure tests are isolated and reproducible.

## Key Features Tested

1. Command Handlers:
   - Start command
   - Authorization flow
   - Contract viewing
   - Payout requests
   - Help command

2. External Clients:
   - Database operations
   - ICP smart contract interactions
   - Open Banking API integration
   - Email notifications

## Mocking Strategy

- Database operations are mocked using SQLAlchemy session mocks
- ICP interactions are mocked at the canister level
- HTTP requests (Open Banking, Mailgun) are mocked using request/response mocks
- Telegram bot interactions are mocked using Update and Context mocks 