# NairaHash

NairaHash is a production-style Bitcoin rewards platform built with Python, FastAPI, and PostgreSQL. It includes:

- Secure user authentication with JWT
- BTC reward task system
- User dashboard and balance tracking
- Withdrawal request workflow
- Admin overview endpoints
- PostgreSQL-ready SQLAlchemy models
- Docker + docker-compose support for local development

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/donwill680-cyber/NairaHash.git
cd NairaHash
```

### 2. Create environment file

```bash
cp .env.example .env
```

### 3. Start PostgreSQL and the API

```bash
docker compose up --build
```

The API will be available at:
- http://localhost:8000/docs
- PostgreSQL: localhost:5432

### 4. Create an admin user

The application does not create an admin user automatically. To make a user admin, update the `is_admin` flag manually in PostgreSQL or seed a user via the database.

## Project structure

```text
app/
  api/
    v1/
  core/
  models/
  schemas/
  services/
  config.py
  db.py
  deps.py
  main.py
Dockerfile
README.md
requirements.txt
docker-compose.yml
.env.example
```

## Features

- User registration and login
- BTC wallet balances and tracking
- Task reward completion engine
- Withdrawal request flow
- Referral-code ready model layer
- Admin endpoint scaffold

## Tech stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- AsyncPG
- JWT auth via python-jose
- Passlib with bcrypt
- Docker Compose

## Notes

This is a solid foundation for a real-world fintech app. For production deployment, you should add:

- Payment/invoice provider integration
- Real BTC market price APIs
- Email verification and OTP flow
- Role-based access controls beyond admin
- Celery/RQ worker tasks for payout processing
- Observability and monitoring
- CI/CD pipeline and automated tests
