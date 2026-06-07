# Environment Variables

Set these variables in Render for production:

| Variable | Required | Example | Purpose |
|---|---|---|---|
| `APP_NAME` | Yes | `StatementIQ` | Branding inside the app |
| `DATABASE_URL` | Yes | `postgresql+psycopg://user:pass@host:5432/dbname` | PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes for AI output | `sk-...` | Enables OpenAI-powered analysis |
| `OPENAI_MODEL` | Yes | `gpt-4.1-mini` | Model used for analysis generation |
| `SECRET_KEY` | Yes | random long string | Reserved for session/security expansion |
| `PORT` | No | `10000` | Provided automatically by Render |

## Recommended Values

- `APP_NAME=StatementIQ`
- `OPENAI_MODEL=gpt-4.1-mini`
- `SECRET_KEY` should be randomly generated and never committed.

## Notes

- If `OPENAI_API_KEY` is missing, the app still runs but falls back to a deterministic local summary instead of model-generated analysis.
- `DATABASE_URL` must point to PostgreSQL in production.
- The app automatically normalizes `postgres://`, `postgresql://`, and `postgresql+psycopg://` forms for Render compatibility.
