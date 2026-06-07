# StatementIQ

StatementIQ is a Streamlit-based SaaS MVP for analyzing annual reports, SEC filings, and core financial statements.

AI-powered financial statement analysis platform for investors, lenders, founders, and analysts.

## Features

- User accounts with email and password login
- Upload PDF and text-based financial documents
- Financial statement extraction
- OpenAI-powered analysis with a structured output
- Financial Health Score, trends, ratios, risks, strengths, and takeaways
- PostgreSQL-backed analysis history
- PDF report export
- Responsive Streamlit interface

## Project Structure

```text
app/
  components/
  db/
  services/
  utils/
assets/
sql/
streamlit_app.py
requirements.txt
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create PostgreSQL database and user, then run:

```bash
psql -d statementiq -f sql/schema.sql
```

4. Copy `.env.example` to `.env` and fill in your values.
5. Start the app:

```bash
streamlit run streamlit_app.py
```

## Notes

- The MVP works best with text-based PDFs.
- If OpenAI output parsing fails, the app falls back to a deterministic local summary so the workflow still completes.

## Render Deployment

Render deployment files are included in this repo:

- [render.yaml](/Users/mrmoeve/Documents/Financial%20IQ/render.yaml)
- [requirements-prod.txt](/Users/mrmoeve/Documents/Financial%20IQ/requirements-prod.txt)
- [docs/render-deployment.md](/Users/mrmoeve/Documents/Financial%20IQ/docs/render-deployment.md)
- [docs/render-postgresql-setup.md](/Users/mrmoeve/Documents/Financial%20IQ/docs/render-postgresql-setup.md)
- [docs/environment-variables.md](/Users/mrmoeve/Documents/Financial%20IQ/docs/environment-variables.md)
