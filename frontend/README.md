# Robust NIDS Frontend

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue?logo=typescript)](https://www.typescriptlang.org/)
[![ShadCN UI](https://img.shields.io/badge/UI-ShadCN-%23ffb4ed?logo=react)](https://ui.shadcn.com/)
[![TanStack Query](https://img.shields.io/badge/Data-TanStack%20Query-%23F18F01?logo=reactquery)](https://tanstack.com/query/latest)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Frontend for **Robust NIDS** — a research-driven, adversarially robust Network Intrusion Detection System built using FastAPI (backend) and Next.js (frontend).

## Project Overview

The **Robust NIDS frontend** provides an interactive web interface for monitoring, analyzing, and visualizing network intrusion data.
It connects to a FastAPI backend to display:

- Real-time intrusion alerts
- Model performance metrics
- Dataset insights and explainability visualizations (e.g., LIME/SHAP)
- Admin and user dashboards for managing NIDS configurations

## Tech Stack

| Layer            | Technology                                                                     |
| ---------------- | ------------------------------------------------------------------------------ |
| Framework        | [Next.js 15](https://nextjs.org/)                                              |
| Language         | [TypeScript](https://www.typescriptlang.org/)                                  |
| Styling          | [Tailwind CSS](https://tailwindcss.com/) + [ShadCN/UI](https://ui.shadcn.com/) |
| Data Fetching    | [TanStack Query](https://tanstack.com/query/latest)                            |
| State Management | React hooks + Query caching                                                    |
| Icons            | [Lucide React](https://lucide.dev/)                                            |
| API Integration  | FastAPI backend (`/api/v1/...`)                                                |

## Setup & Installation

### Clone Repository

```bash
git clone https://github.com/Fidelisaboke/robust-nids.git
cd robust-nids/frontend
```

### Install Dependencies

```bash
npm install
# or
pnpm install
```

### Configure Environment Variables

```bash
cp .env.local.example .env.local
```

Set your backend API base URL (usually):

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Run Development Server

```bash
npm run dev
```

Visit ➜ [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── .gitignore
├── README.md
├── components.json
├── eslint.config.mjs
├── next.config.ts
├── package-lock.json
├── package.json
├── postcss.config.mjs
├── public
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
├── src
│   ├── app
│   │   ├── (admin)
│   │   │   └── admin
│   │   │       ├── audit-logs
│   │   │       │   └── page.tsx
│   │   │       ├── roles
│   │   │       │   └── page.tsx
│   │   │       ├── system-config
│   │   │       │   └── page.tsx
│   │   │       └── users
│   │   │           └── page.tsx
│   │   ├── (auth)
│   │   │   ├── layout.tsx
│   │   │   ├── login
│   │   │   │   ├── page.tsx
│   │   │   │   └── verify-mfa
│   │   │   │       └── page.tsx
│   │   │   ├── reset-password
│   │   │   │   └── page.tsx
│   │   │   ├── totp-setup
│   │   │   │   └── page.tsx
│   │   │   └── verify-email
│   │   │       └── page.tsx
│   │   ├── (dashboard)
│   │   │   ├── alerts
│   │   │   │   └── page.tsx
│   │   │   ├── dashboard
│   │   │   │   └── page.tsx
│   │   │   ├── layout.tsx
│   │   │   ├── metrics
│   │   │   │   └── page.tsx
│   │   │   ├── network-map
│   │   │   │   └── page.tsx
│   │   │   ├── reports
│   │   │   │   └── page.tsx
│   │   │   ├── settings
│   │   │   │   └── page.tsx
│   │   │   └── threat-intelligence
│   │   │       └── page.tsx
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components
│   │   └── ui
│   │       ├── button.tsx
│   │       └── sonner.tsx
│   ├── contexts
│   │   └── AuthContext.tsx
│   ├── hooks
│   │   └── useAuthMutations.ts
│   ├── middleware.ts
│   ├── providers
│   │   └── QueryProvider.tsx
│   └── types
│       ├── auth.ts
│       └── index.ts
└── tsconfig.json

```

## Environment Variables

| Variable              | Description                     | Example                 |
| --------------------- | ------------------------------- | ----------------------- |
| `NEXT_PUBLIC_API_URL` | Base URL of the FastAPI backend | `http://127.0.0.1:8000` |

## Scripts

| Command          | Description                |
| ---------------- | -------------------------- |
| `npm run dev`    | Start the local dev server |
| `npm run build`  | Build for production       |
| `npm start`      | Run production server      |
| `npm run lint`   | Lint the codebase          |
| `npm run format` | Auto-format using Prettier |

## Code Quality

### Linting

```bash
npm run lint
```

### Formatting

```bash
npx prettier . --write
```

_(Auto-runs via pre-commit hook if configured)_

## API Integration

All API requests use `TanStack Query` and a centralized `apiClient` instance for caching, error handling, and retries.

Example usage:

```tsx
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

function useFetchAlerts() {
  return useQuery({
    queryKey: ["alerts"],
    queryFn: () => apiClient.get("/alerts").then((res) => res.data),
  });
}
```

## Development Workflow

| Step | Action                                                               |
| ---- | -------------------------------------------------------------------- |
| 1    | Start PostgreSQL locally (`sudo service postgresql start`)           |
| 2    | Run FastAPI backend (`uv run uvicorn api.main:app --reload`)         |
| 3    | Start frontend (`npm run dev`)                                       |
| 4    | Use TanStack Query DevTools (`localhost:3000/__query`)               |
| 5    | Format and lint before committing (`npm run lint && npm run format`) |

## Deployment

For production:

```bash
npm run build
npm start
```

Recommended platforms:

- [**Vercel**](https://vercel.com) (Next.js native)
- [**Render**](https://render.com) (full-stack deployment with FastAPI backend)
- [**Docker**] – multi-stage build with Nginx

## Testing

_(Optional integration testing planned with Playwright or Vitest)_

## Contributing

Contributions are welcome!
Please follow the [pre-commit](https://pre-commit.com/) and [detect-secrets](https://github.com/Yelp/detect-secrets) setup in `docs/SETUP.md`.

## License

This project is licensed under the **MIT License** — see the [LICENSE](../LICENSE) file for details.

## Acknowledgements

- [Next.js](https://nextjs.org)
- [ShadCN/UI](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query/latest)
- [Lucide Icons](https://lucide.dev)
- [FastAPI](https://fastapi.tiangolo.com)
