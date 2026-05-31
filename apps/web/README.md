# Payday Web

Next.js (App Router) + TypeScript + Tailwind CSS frontend for Payday. It serves
two natively separated user contexts plus an onboarding wizard, and ships a
self-contained **Demo Day** experience.

| Context | Route group | Surface |
| --- | --- | --- |
| **Employer dashboard** | `src/app/(employer)` | One-Tap Payroll dashboard, employees, history, setup wizard. |
| **Mobile staff portal** | `src/app/(staff)` | Login-gated phone-width portal: payslips, downloads, earnings record. |

## Highlights

- **Onboarding wizard** (`/onboarding`) — a 4-step flow (Business → Team →
  Payouts → Review) to configure a business, employees, salaries and wallet
  funding in under 10 minutes. Includes a one-click "Load demo team".
- **One-Tap Payroll Dashboard** (`/dashboard`) — the centre of the app: funded
  ALATPay Payroll Wallet balance, active staff roster, and a prominent
  **Run Payroll** button.
- **Live Demo Day sequence** — seeded with **Mama Tunde's Pharmacy** (5 workers,
  wallet pre-funded with exactly ₦415,000). Pressing Run Payroll transitions all
  five rows Pending → Sending → Paid across a crisp ~8s window, ticking the
  wallet down live.
- **Automated payslip alerts** — as each worker is paid, a mock WhatsApp/SMS
  payslip (gross statement + unique ALATPay reference) is dispatched and shown in
  the dashboard alerts feed.
- **Staff portal** — workers log in independently, view and **download** their
  payslips, and export a **verified earnings statement** to unlock loans/tenancy.

## State model

A tiny shared store (`src/lib/store.ts`, built on React's `useSyncExternalStore`)
is persisted to `localStorage` and synchronised across tabs via the `storage`
event. A payroll run on the dashboard therefore streams "in real time" into any
open staff-portal tab. The payroll simulation lives in
`src/lib/payroll-engine.ts`; the Demo Day seed in `src/lib/seed.ts`.

```
src/
├── app/
│   ├── (employer)/{dashboard,onboarding}/...
│   └── (staff)/portal/{login,payslips/[id],profile}/...
├── components/{employer,onboarding,staff,ui}/...
└── lib/
    ├── store.ts            # shared persistent store + hooks
    ├── seed.ts             # Mama Tunde's Pharmacy demo data
    ├── payroll-engine.ts   # Pending→Sending→Paid simulation (8s)
    ├── notifications.ts     # mock WhatsApp/SMS payslip dispatch
    ├── models.ts           # client domain types
    ├── api.ts / types.ts   # typed backend client
    └── format.ts
```

## Quick start

```bash
cd apps/web
npm install
npm run dev                      # http://localhost:3000
```

- `/` — landing
- `/onboarding` — setup wizard
- `/dashboard` — One-Tap Payroll dashboard (Demo Day ready)
- `/portal` — staff portal (redirects to `/portal/login`)

## Scripts

```bash
npm run dev      # dev server
npm run build    # production build (also type-checks)
npm run lint     # eslint
```
