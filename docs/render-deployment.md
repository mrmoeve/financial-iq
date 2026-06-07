# Render Deployment Guide

This guide deploys StatementIQ to Render using the included [render.yaml](/Users/mrmoeve/Documents/Financial%20IQ/render.yaml).

## Files Included

- [render.yaml](/Users/mrmoeve/Documents/Financial%20IQ/render.yaml)
- [requirements-prod.txt](/Users/mrmoeve/Documents/Financial%20IQ/requirements-prod.txt)
- [start.sh](/Users/mrmoeve/Documents/Financial%20IQ/start.sh)
- [docs/environment-variables.md](/Users/mrmoeve/Documents/Financial%20IQ/docs/environment-variables.md)
- [docs/render-postgresql-setup.md](/Users/mrmoeve/Documents/Financial%20IQ/docs/render-postgresql-setup.md)

## Deploy with Blueprint

1. Push this repository to GitHub.
2. In Render, click `New +`.
3. Choose `Blueprint`.
4. Connect the GitHub repository: `mrmoeve/financial-iq`.
5. Render detects [render.yaml](/Users/mrmoeve/Documents/Financial%20IQ/render.yaml).
6. Review the resources:
   - Web service: `statementiq`
   - PostgreSQL database: `statementiq-db`
7. Add your secret:
   - `OPENAI_API_KEY`
8. Click `Apply`.

## Render Build and Start Commands

- Build command: `pip install -r requirements-prod.txt`
- Start command: `bash start.sh`

## Post-Deploy Checks

1. Open the deployed service URL.
2. Create a test user account.
3. Upload a text-based PDF or `.txt` sample.
4. Confirm:
   - login works
   - analysis history is saved
   - PDF export downloads
   - OpenAI results appear when `OPENAI_API_KEY` is configured

## Manual Deploy Alternative

If you prefer not to use Blueprint:

1. Create a Render PostgreSQL database first.
2. Create a new Web Service from the GitHub repo.
3. Set runtime to `Python`.
4. Use:
   - Build command: `pip install -r requirements-prod.txt`
   - Start command: `bash start.sh`
5. Add the environment variables listed in [docs/environment-variables.md](/Users/mrmoeve/Documents/Financial%20IQ/docs/environment-variables.md).
6. Set `DATABASE_URL` to the Render Postgres connection string.

## Operational Notes

- The app creates tables automatically on startup if the database is reachable.
- Streamlit is served on Render’s assigned port through `start.sh`.
- For scanned PDFs, you may want to add OCR in a future release because the current MVP is optimized for text-based files.
