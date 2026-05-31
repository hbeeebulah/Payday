# Payday

Payday is a payroll management platform that gives Nigerian small business
owners the ability to pay every employee simultaneously with a single tap, on
time, every month, with automatic payslips and a clean digital record of every
salary ever paid.

## Monorepo

```
payday/
├── apps/
│   ├── web/        # Next.js (App Router) + TypeScript + Tailwind CSS frontend
│   └── api/        # Python FastAPI backend (async, SQLAlchemy, Alembic)
├── package.json    # npm workspaces root
└── README.md
```

### `apps/web` — frontend

Next.js frontend serving two natively separated user contexts via route groups:

- **Employer management dashboard** (`src/app/(employer)`) — desktop-oriented
  panels for managing employees and running payroll.
- **Mobile-optimized staff portal** (`src/app/(staff)`) — phone-width portal
  where staff view their salary, payslips and profile.

Styled with Tailwind CSS for a clean, distraction-free, professional interface.
See [`apps/web/README.md`](apps/web/README.md).

### `apps/api` — backend

Python **FastAPI** service built for concurrency — it processes parallel API
requests and asynchronous ALATPay webhook ingestion. It owns the relational
schema (SQLAlchemy), the migrations (Alembic), and an isolated ALATPay service.
See [`apps/api/README.md`](apps/api/README.md).

#### Relational schema (SQLAlchemy)

| Table | Purpose |
| --- | --- |
| `businesses` | Company metadata for each employer. |
| `employees` | Personal details, assigned corporate role, exact salary level, bank account number and routing details. |
| `payroll_runs` | A "pay everyone" execution: execution timestamp, cumulative funding total, status. |
| `transaction_receipts` | A permanent per-employee payout log: amount, unique ALATPay transaction reference and the specific distribution state. |

#### Directory separation

The backend cleanly separates concerns:

```
apps/api/app/
├── routes/                 # backend routes (incl. /webhooks/alatpay ingestion)
├── models/                 # SQLAlchemy schema
├── services/alatpay/       # ISOLATED service class dedicated to ALATPay only
└── ...
apps/api/alembic/versions/  # migration files
```

## Getting started

Backend:

```bash
cd apps/api
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev          # http://localhost:3000
```

Or from the repo root: `npm run dev:web` and `npm run dev:api`.

## Tech stack

- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, httpx
- **Database:** PostgreSQL (prod) / SQLite (local dev) via async drivers
- **Payments:** ALATPay (Wema Bank)
