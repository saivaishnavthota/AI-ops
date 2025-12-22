# AI-Ops Platform

AI-Powered Managed Services Operations Platform for incident management, alert handling, and automated remediation.

## Tech Stack

- **Frontend**: React 18 + TypeScript + Ant Design 5 + Redux Toolkit
- **Backend**: FastAPI + Python 3.11 + SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15 + Redis 7
- **Task Queue**: Celery with Redis broker
- **Deployment**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. **Clone and configure environment**

```bash
cd "AI-powered managed services"
cp .env.example .env
# Edit .env with your settings
```

2. **Start with Docker Compose (Development)**

```bash
# Start all services with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

3. **Access the application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development (Without Docker)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL and Redis (or use Docker)
docker-compose up postgres redis -d

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### Build and Deploy

```bash
# Build production images
docker-compose build

# Start production stack
docker-compose up -d

# View logs
docker-compose logs -f
```

### Database Migrations

```bash
# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head
```

## Project Structure

```
ai-powered managed services/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── config/         # Configuration
│   │   ├── core/           # Security, JWT
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── workers/        # Celery tasks
│   ├── alembic/            # Database migrations
│   └── Dockerfile
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── app/           # Store, routes
│   │   ├── components/    # UI components
│   │   ├── features/      # Feature modules
│   │   ├── hooks/         # Custom hooks
│   │   ├── store/         # Redux + RTK Query
│   │   └── types/         # TypeScript types
│   └── Dockerfile
│
├── nginx/                  # Nginx configuration
├── scripts/               # Utility scripts
├── docker-compose.yml     # Production compose
├── docker-compose.dev.yml # Development compose
└── .env.example          # Environment template
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register organization
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Current user

### Incidents
- `GET /api/v1/incidents` - List incidents
- `POST /api/v1/incidents` - Create incident
- `GET /api/v1/incidents/{id}` - Get incident
- `PUT /api/v1/incidents/{id}` - Update incident
- `POST /api/v1/incidents/{id}/acknowledge` - Acknowledge
- `POST /api/v1/incidents/{id}/resolve` - Resolve

### Alerts
- `GET /api/v1/alerts` - List alerts
- `POST /api/v1/alerts` - Ingest alert
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge
- `POST /api/v1/alerts/{id}/resolve` - Resolve
- `POST /api/v1/alerts/{id}/create-incident` - Create incident

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `SECRET_KEY` - JWT signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CORS_ORIGINS` - Allowed frontend origins

## License

Proprietary - All rights reserved.
