# Payday Web

Next.js (App Router) + TypeScript + Tailwind CSS frontend for Payday. It serves
two distinct, natively separated user contexts via route groups:

| Context | Route group | Surface |
| --- | --- | --- |
| **Employer management dashboard** | `src/app/(employer)` | Desktop-oriented panels: overview, employees, payroll runs. |
| **Mobile-optimized staff portal** | `src/app/(staff)` | Phone-width portal: salary summary, payslips, profile. |

## Layout

```
src/
├── app/
│   ├── layout.tsx              # root layout + metadata
│   ├── page.tsx                # public landing page
│   ├── globals.css             # Tailwind entry
│   ├── (employer)/             # employer dashboard context
│   │   ├── layout.tsx              # sidebar shell
│   │   └── dashboard/
│   │       ├── page.tsx            # overview
│   │       ├── employees/page.tsx
│   │       └── payroll/page.tsx
│   └── (staff)/                # staff portal context
│       ├── layout.tsx              # mobile shell + bottom nav
│       └── portal/
│           ├── page.tsx            # home
│           ├── payslips/page.tsx
│           └── profile/page.tsx
├── components/                 # UI + per-context components
└── lib/                        # API client, types, formatting, demo data
```

## Quick start

```bash
cd apps/web
npm install
cp .env.example .env.local       # point API_PROXY_URL at the FastAPI backend
npm run dev                      # http://localhost:3000
```

- `/` — landing page
- `/dashboard` — employer management dashboard
- `/portal` — mobile-optimized staff portal

## Backend connectivity

`next.config.mjs` rewrites `/api/*` to the FastAPI backend (`API_PROXY_URL`,
default `http://localhost:8000`). The typed client in `src/lib/api.ts` calls the
backend through that proxy. The scaffolded pages currently render from
`src/lib/demo-data.ts`; swap those reads for the `api` client to go live.

## Scripts

```bash
npm run dev      # dev server
npm run build    # production build (also type-checks)
npm run lint     # eslint
```
