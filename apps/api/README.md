# Payday API

FastAPI backend that orchestrates simultaneous salary disbursement for small
businesses via **ALATPay**. Built for high concurrency: a single async engine,
per-request `AsyncSession`s, parallel disbursement, and async webhook ingestion.

## Layout

```
app/
├── main.py                 # FastAPI app factory + middleware
├── core/config.py          # environment-driven settings
├── db/                     # async engine, session, declarative base
├── models/                 # SQLAlchemy ORM models (the relational schema)
│   ├── business.py             # Business — company metadata
│   ├── employee.py             # Employee — personal/role/salary/bank details
│   ├── payroll_run.py          # PayrollRun — batch execution + funding totals
│   └── transaction_receipt.py  # TransactionReceipt — per-employee payout log
├── schemas/                # Pydantic request/response models
├── routes/                 # HTTP routes (businesses, employees, payroll, webhooks)
└── services/
    ├── payroll.py          # payroll orchestration
    └── alatpay/            # ISOLATED ALATPay integration (the only caller)
alembic/                    # database migrations
tests/                      # pytest suite (ASGI integration + unit)
```

## Quick start

```bash
cd apps/api
pip install -r requirements-dev.txt        # or requirements.txt for prod
cp .env.example .env                        # then fill in ALATPay credentials

# Run migrations (defaults to local async SQLite if DATABASE_URL is unset)
alembic upgrade head

# Start the dev server
uvicorn app.main:app --reload --port 8000
```

Interactive API docs are served at `http://localhost:8000/docs`.

## Database

- ORM: **SQLAlchemy 2.0** (async, typed `Mapped[...]` columns).
- Production: PostgreSQL via `asyncpg`. Local/dev/test: async SQLite via `aiosqlite`.
- Migrations: **Alembic** (async `env.py`, URL injected from app settings).

## ALATPay integration

All provider communication is confined to `app/services/alatpay/`:

- `client.py` — thin async HTTP transport.
- `service.py` — `AlatPayService`: batch disbursement (parallel, bounded
  concurrency), status reconciliation, and HMAC webhook verification.
- `models.py` / `exceptions.py` — typed contracts and error hierarchy.

The rest of the app only depends on `AlatPayService`, so the provider can be
mocked or swapped without touching business logic.

## Tests & lint

```bash
pytest            # ASGI integration + ALATPay unit tests
ruff check .      # lint
```
