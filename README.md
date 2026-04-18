# Urban Renewal SaaS (FastAPI + React + SQL Server)

Production-oriented SaaS scaffold for managing urban renewal (פינוי-בינוי) projects in Israel.

## Stack

- Backend: FastAPI + SQLAlchemy + Alembic + JWT/OAuth2
- Frontend: React + TypeScript (Vite)
- Database: SQL Server
- DevOps: Docker + docker-compose

## Repository structure

```text
backend/
  app/
    ai/
    api/
      routes/
    auth/
    billing/
    core/
    db/
    models/
    schemas/
    services/
    utils/
    main.py
  alembic/
  requirements.txt
  Dockerfile

frontend/
  src/
    api/
    components/
    context/
    hooks/
    pages/
    routes/
    types/
    utils/
  package.json
  Dockerfile

docker-compose.yml
```

## Quick start

### 1) Run with Docker

```bash
docker compose up --build
```

Services:
- API: http://localhost:8000
- Frontend: http://localhost:5173
- SQL Server: localhost:1433

### 2) Backend local run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3) Frontend local run

```bash
cd frontend
npm install
npm run dev
```

## Migrations

Alembic is configured in `backend/alembic.ini`.

Create a migration:

```bash
cd backend
alembic revision --autogenerate -m "your message"
```

Apply migrations:

```bash
alembic upgrade head
```

## Notes

- Seeded on startup: roles/permissions and default billing plans.
- Billing enforces freemium + developer-stage lock + professional/add-on capabilities.
- External integrations (signature, WhatsApp/email, AI modules) are mocked/stubbed with extensible service interfaces.
