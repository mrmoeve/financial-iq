# LinkedIn Job Search Tracker

LinkedIn Job Search Tracker is a Next.js app that connects to Gmail, detects job-search activity, stores it in SQLite, and renders a dashboard plus an NYS work-search PDF export.

## Features

- Google OAuth authentication
- Gmail read-only sync for LinkedIn and common recruiting systems
- Detection for:
  - Job applications
  - Application confirmations
  - Interview invitations
  - Recruiter outreach
- Field extraction for date, company, job title, recruiter name, and interview date
- SQLite storage using `better-sqlite3`
- Dashboard metrics for total applications, weekly applications, interviews, recruiter contacts, and companies applied to
- NYS work-search PDF export
- Vercel cron endpoint for scheduled sync

## Local Setup

1. Install dependencies:

```bash
npm install
```

2. Copy `.env.example` to `.env.local` and set:

```bash
AUTH_SECRET=
AUTH_GOOGLE_ID=
AUTH_GOOGLE_SECRET=
NEXTAUTH_URL=http://localhost:3000
CRON_SECRET=
GMAIL_SYNC_LOOKBACK_DAYS=30
```

3. In Google Cloud Console:

- Enable Gmail API
- Configure a Google OAuth web application
- Add `http://localhost:3000/api/auth/callback/google` as an authorized redirect URI

4. Start the app:

```bash
npm run dev
```

5. Sign in with Google and click `Sync Gmail`.

## Production Notes

- The app stores data in a local SQLite file named `job-tracker.db`.
- Vercel’s filesystem is ephemeral, so SQLite is suitable for local development and non-persistent previews.
- For durable Vercel production storage, keep the current repository layout and swap the repository layer to a hosted SQLite-compatible service such as Turso or to Vercel Postgres.
- Add your production callback URI:
  - `https://YOUR_DOMAIN/api/auth/callback/google`
- Protect the cron endpoint by setting `CRON_SECRET` and sending `Authorization: Bearer YOUR_SECRET`.

## Routes

- `/` dashboard
- `/signin` Google sign-in
- `/api/sync` manual Gmail sync
- `/api/cron/sync` scheduled sync
- `/api/report` NYS PDF export
