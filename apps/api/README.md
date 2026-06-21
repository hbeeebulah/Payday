# Payday API

FastAPI backend that orchestrates simultaneous salary disbursement for small
businesses. Built for high concurrency: a single async engine, per-request
`AsyncSession`s, parallel disbursement, and async webhook ingestion.

## Layout

```
app/
├── main.py                 # FastAPI app factory + middleware
├── core/config.py          # environment-driven settings (incl. ALATPay + payout)
├── db/                     # async engine, session, declarative base
├── models/                 # SQLAlchemy ORM models (the relational schema)
│   ├── business.py · employee.py · payroll_run.py · transaction_receipt.py
│   └── payroll_wallet.py   # per-business ALATPay static wallet
├── schemas/                # Pydantic request/response models
├── routes/                 # businesses, employees, wallets, payroll, analytics, webhooks
└── services/
    ├── wallet.py · payroll.py · analytics.py
    └── alatpay/            # ISOLATED provider integration (only caller of ALATPay/Wema)
        ├── client.py · service.py · wallets.py · settlements.py · models.py
        └── payout/         # REAL Wema Merchant Payout (NIP disbursement)
            ├── crypto.py       # AES/CBC/PKCS7 envelope
            ├── client.py       # token auth + encrypted transport
            ├── service.py      # banks, name enquiry, balance, transfer, status
            ├── adapter.py      # exposes payout as a disbursement backend
            └── models.py       # contracts + NIP response-code mapping
alembic/                    # database migrations
tests/                      # pytest suite (ASGI integration + unit) with fakes
```

## Disbursement backends

`DISBURSEMENT_MODE` selects how a payroll run actually moves money. Both backends
expose the same interface (`disburse_batch` / `get_transaction_status`), so the
payroll orchestration is identical regardless of backend.

### `collection` (default — sandbox/demo)
The ALATPay collection rails (`service.py`): Pay with Bank Transfer, with an
explicit branch to Pay with Bank Details (Wema direct debit) for bank code `035`.

### `payout` (real NIP disbursement)
The **Wema Merchant Payout API** (`payout/` subpackage) sends money OUT to any
Nigerian bank account over NIBSS Instant Payment. It is a distinct product from
the collection APIs:

- **Auth** — `POST /api/Authentication/authenticate` returns a JWT (24h) + refresh
  token. The client caches the token (with an `asyncio` lock so parallel payouts
  authenticate once) and sends `Authorization: Bearer` + `VendorId` headers.
- **Encryption** — every business payload is `AES/CBC/PKCS7` encrypted, base64
  encoded, and wrapped in a named field (`FundTransferRequest`, `NameEnquiryRequest`,
  …). Responses are encrypted too. See `payout/crypto.py`.
- **Operations** — `GetNIPBanks`, `NIPNameEnquiry`, **`NIPFundTransfer`** (the
  payout), `GetTransactionStatus`, `GetBalance`. NIP response codes are mapped to
  distribution states in `payout/models.py` (`00` = paid; `01/09/20` = pending).

To go live set `DISBURSEMENT_MODE=payout` and the `PAYOUT_*` variables (issued by
your Wema liaison — username/password, vendor id, per-merchant AES key/IV, source
account, optional APIM subscription key). See `.env.example`.

> The default `PAYOUT_ENCRYPTION_KEY` / `PAYOUT_ENCRYPTION_IV` are the **public
> sandbox** values and must be replaced in production. A few endpoint paths and
> the amount denomination should be confirmed with your bank liaison before
> go-live (documented inline in `payout/client.py`).

## Quick start

```bash
cd apps/api
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head                        # local default: async SQLite
uvicorn app.main:app --reload --port 8000
```

Interactive API docs at `http://localhost:8000/docs`.

## Tests & lint

```bash
pytest            # ASGI integration + ALATPay/payout unit tests (network stubbed)
ruff check .      # lint
```
