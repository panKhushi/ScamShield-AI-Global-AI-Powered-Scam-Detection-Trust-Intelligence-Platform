This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Environment variables

Create `frontend/.env.local` for local development. Configure the same variables in
Render's environment settings before building the service:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-supabase-publishable-or-anon-key
BACKEND_URL=http://127.0.0.1:8000
```

For the deployed frontend, set `BACKEND_URL` to:

```env
BACKEND_URL=https://scamshield-ai-global-ai-powered-scam.onrender.com
```

`NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` are required
at build time. Use the public publishable/anon key only; never expose a Supabase
service-role key or JWT secret in frontend variables.

The frontend sends API requests through `/backend`. `BACKEND_URL` is used by the
Next.js rewrite in `next.config.ts`, so it must be configured before a production
build.

## Render deployment

Deploy this project as a **Web Service**, not a Static Site. The authentication
proxy in `proxy.ts` and the `/backend` rewrite in `next.config.ts` require the
Next.js server runtime.

Use these Render settings:

```text
Root Directory: frontend
Build Command: npm install && npm run build
Start Command: npm run start
```

Do not set a publish directory. `next build` creates `.next`, and `next start`
serves that production build.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
