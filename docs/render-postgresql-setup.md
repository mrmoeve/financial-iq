# Render PostgreSQL Setup

StatementIQ uses PostgreSQL for user accounts and analysis history.

## Option 1: Create the database with `render.yaml`

If you deploy with the included [render.yaml](/Users/mrmoeve/Documents/Financial%20IQ/render.yaml), Render will provision:

- A web service named `statementiq`
- A PostgreSQL database named `statementiq-db`

The `DATABASE_URL` environment variable is injected automatically from that managed database.

## Option 2: Create the database manually in Render

1. In Render, click `New +`.
2. Choose `PostgreSQL`.
3. Set:
   - Name: `statementiq-db`
   - Database: `statementiq`
   - Region: same region as your web service
   - Plan: `Starter` or higher
4. Create the database.
5. Copy the internal or external connection string into the web service `DATABASE_URL` environment variable.

## Schema Initialization

StatementIQ automatically calls SQLAlchemy `create_all()` at app startup, so the core tables are created when the app boots successfully against PostgreSQL.

The application expects these tables:

- `users`
- `analyses`

If you ever want to initialize the schema manually, use:

```sql
\i sql/schema.sql
```

or run:

```bash
psql "$DATABASE_URL" -f sql/schema.sql
```

## Required Postgres Notes

- Use a PostgreSQL connection string, not SQLite.
- Keep the database in the same region as the app to reduce latency.
- Render may provide a `postgres://` URL; SQLAlchemy/psycopg generally works best when the value is stored as a standard PostgreSQL URL in `DATABASE_URL`.
