# Payday API

FastAPI backend that orchestrates simultaneous salary disbursement for small
businesses via **ALATPay**. Built for high concurrency: a single async engine,
per-request `AsyncSession`s, parallel disbursement, and async webhook ingestion.

## Layout

```
app/
├── main.py                 # FastAPI app factory + middleware
├── core/config.py          # environment-driven settings (incl. ALATPay creds)
├── db/                     # async engine, session, declarative base
├── models/                 # SQLAlchemy ORM models (the relational schema)
│   ├── business.py             # Business — company metadata
│   ├── employee.py             # Employee — personal/role/salary/bank details
│   ├── payroll_wallet.py       # PayrollWallet — per-business ALATPay static wallet
│   ├── payroll_run.py          # PayrollRun — batch execution + funding totals
│   └── transaction_receipt.py  # TransactionReceipt — per-employee payout log
├── schemas/                # Pydantic request/response models
├── routes/                 # HTTP routes
│   ├── businesses.py / employees.py
│   ├── wallets.py              # provision + balance for the Payroll Wallet
│   ├── payroll.py              # create + (background) execute payroll runs
│   ├── analytics.py            # monthly payroll analytics + settlements
│   └── webhooks.py             # ALATPay Transaction Monitoring ingestion
└── services/
    ├── wallet.py           # Payroll Wallet orchestration + overdraft guard
    ├── payroll.py          # payroll orchestration + background disbursement
    ├── analytics.py        # monthly analytics from the local ledger
    └── alatpay/            # ISOLATED ALATPay integration (the only caller)
        ├── client.py           # async transport; header + businessId injection
        ├── service.py          # disbursement rails + webhook parsing
        ├── wallets.py          # Static Wallets API (provision / balance)
        ├── settlements.py      # Settlements API wrapper
        ├── models.py           # typed request/result contracts
        └── exceptions.py
alembic/                    # database migrations
tests/                      # pytest suite (ASGI integration + unit) with fakes
```

## ALATPay engine

All provider communication is confined to `app/services/alatpay/`. The transport
client injects credentials securely on every call — the subscription key as the
`Ocp-Apim-Subscription-Key` header and the merchant `businessId` into the body /
query string.

- **Static Wallets** (`wallets.py`) — provisions a dedicated **Payroll Wallet**
  (a static ALATPay account) per business and reads its balance. The balance is
  cached on `PayrollWallet.available_balance` and re-checked before every run as
  an **overdraft guard** (`services/wallet.py`).
- **Disbursement** (`service.py`) — pays each worker on the correct rail:
  - **Pay with Bank Transfer** for general accounts;
  - **Pay with Bank Details** (Wema direct debit, bank code `035`) for Wema
    accounts — selected by an explicit branch in `disburse_one`.
  - `disburse_batch` fans out the payouts **in parallel** (bounded concurrency).
- **Background execution** — `POST /payroll-runs/{id}/execute` runs the overdraft
  check synchronously, then hands the parallel ALATPay calls to a FastAPI
  `BackgroundTasks` worker (`run_payroll_disbursement_task`).
- **Webhooks** (`routes/webhooks.py`) — `POST /webhooks/alatpay` ingests
  Transaction Monitoring callbacks, re-verifies the status server-side, locates
  the matching `TransactionReceipt` and flips it from pending to **paid**.
- **Settlements & analytics** (`settlements.py`, `services/analytics.py`) — wraps
  the Settlements API and computes monthly payroll spend for owner visibility.

> Note: ALATPay does not document a webhook signing scheme, so the webhook body
> is not trusted on its own — the handler re-confirms each transaction via the
> Transactions API. An optional `ALATPAY_WEBHOOK_SECRET` enables HMAC checking if
> you front the endpoint with your own signer.

## Quick start

```bash
cd apps/api
pip install -r requirements-dev.txt        # or requirements.txt for prod
cp .env.example .env                        # then fill in ALATPay credentials

alembic upgrade head                        # local default: async SQLite
uvicorn app.main:app --reload --port 8000
```

Interactive API docs are served at `http://localhost:8000/docs`.

## Key endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/businesses/{id}/wallet` | Provision the Payroll Wallet |
| GET | `/businesses/{id}/wallet?refresh=true` | Wallet details + live balance |
| POST | `/businesses/{id}/payroll-runs` | Create a run (one receipt per employee) |
| POST | `/businesses/{id}/payroll-runs/{run}/execute` | Overdraft check + background disburse |
| POST | `/webhooks/alatpay` | Transaction Monitoring callback ingestion |
| GET | `/businesses/{id}/analytics/payroll` | Monthly analytics + settlements |

## Tests & lint

```bash
pytest            # ASGI integration + unit tests (ALATPay stubbed via fakes)
ruff check .      # lint
```
