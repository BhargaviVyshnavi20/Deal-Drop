# 📉 DealDrop — Intelligent E-Commerce Price Tracker & Drop Alert System

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Firecrawl](https://img.shields.io/badge/Firecrawl-FF6B35?style=for-the-badge)](https://www.firecrawl.dev/)
[![Resend](https://img.shields.io/badge/Resend-000000?style=for-the-badge&logo=resend&logoColor=white)](https://resend.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

DealDrop is a production-grade, full-stack automated price tracking platform. It monitors e-commerce product prices across major online stores (Amazon, Flipkart, and more), maintains historical price records with interactive trend visualizations, and sends instant automated email alerts whenever a tracked product reaches a new all-time low price.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Screenshots & UI Preview](#-screenshots--ui-preview)
- [System Architecture & Workflow](#-system-architecture--workflow)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [API Reference](#-api-reference)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Product & Price Endpoints](#product--price-endpoints)
- [Environment Configuration](#-environment-configuration)
  - [Backend Configuration (`backend/.env`)](#backend-configuration-backendenv)
  - [Frontend Configuration (`frontend/.env`)](#frontend-configuration-frontendenv)
- [Getting Started & Setup](#-getting-started--setup)
  - [Option 1: Docker Compose (Quickstart)](#option-1-docker-compose-quickstart)
  - [Option 2: Modular Local Setup](#option-2-modular-local-setup)
- [Automated Testing & CI/CD](#-automated-testing--cicd)
- [License](#-license)

---

## 📖 Overview

Online shoppers frequently miss price drops, flash sales, and discounts because manual monitoring across e-commerce platforms is tedious and inconsistent. **DealDrop** automates this entire lifecycle:

1. **Effortless Product Ingestion**: Paste any product URL to extract title, current price, currency, and product images in real time using the Firecrawl LLM-powered scraping engine.
2. **Historical Price Intelligence**: Logs all price observations into PostgreSQL with time-series history for statistical analysis (lowest price, highest price, net percentage fluctuation).
3. **Background Scheduled Tracking**: Asynchronous cron jobs periodically check all tracked listings for price updates.
4. **Intelligent Drop Alerts**: Dispatches transactional emails via Resend when a price drops below its historical minimum.
5. **Modern Dashboard Experience**: Intuitive dark/light UI with real-time feedback, interactive Recharts graphs, and authentication (Local JWT + Google OAuth 2.0).

---

## ✨ Key Features

- **⚡ Instant URL-Based Ingestion**: Paste an e-commerce link and let Firecrawl extract structured product information automatically.
- **📈 Interactive Price Charts**: Visual history charts powered by Recharts with dynamic price delta indicators (▲ Increase / ▼ Decrease / — Stable).
- **⏰ Automated Background Scheduler**: Integrated APScheduler running asynchronous cron jobs to refresh product pricing without blocking web requests.
- **✉️ Automated Lowest-Price Alerts**: Automatic trigger-based transactional email notifications via Resend when prices drop to a new recorded low.
- **🔐 Multi-Method Authentication**:
  - Email/Password authentication with Argon2 password hashing and JWT access tokens.
  - Google OAuth 2.0 Single Sign-On (SSO) integration.
  - Secure tokenized password reset flow with expiring one-time hashes and email delivery.
- **🌓 Adaptive Theming**: Built-in dark and light theme switcher with persistent local storage preferences.
- **🐳 Full Containerization**: Multi-service Docker Compose orchestration with PostgreSQL 16 Alpine, FastAPI, and Vite React frontend.
- **🛡️ Quality & CI/CD**: Automated GitHub Actions CI pipeline executing end-to-end async backend test suites with a live PostgreSQL service container, frontend builds, and Docker image validation.

---

## 📸 Screenshots & UI Preview

### Landing Page & Product Tracking Hero
<p align="center">
  <img width="959" height="475" alt="DealDrop Landing Page" src="https://github.com/user-attachments/assets/1b4ed88d-68fa-4ef2-9669-8a2aad3475a0" />
</p>

### Tracked Products Dashboard
<p align="center">
  <img width="956" height="475" alt="Product Tracking Dashboard" src="https://github.com/user-attachments/assets/a25f7397-af57-4f3e-8390-912d62945d4c" />
</p>

### Interactive Price History & Trends
<p align="center">
  <img width="954" height="472" alt="Price History Charts" src="https://github.com/user-attachments/assets/6ba58bc9-a152-464e-9fab-b9ce668be116" />
</p>

---

## 🔄 System Architecture & Workflow

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (React + Vite)"]
        UI[User Dashboard & Theme Engine]
        AUTH_UI[Auth Modal / Google SSO]
        CHART[Recharts Price Trends]
    end

    subgraph Backend ["Backend (FastAPI REST API)"]
        API[FastAPI Gateway]
        AUTH_SVC[Auth & Security Service]
        TRACK_SVC[Price Tracker Service]
        SCHED[APScheduler Background Job]
        EMAIL_SVC[Resend Email Service]
    end

    subgraph External ["External Services"]
        FC[Firecrawl Scraping API]
        GOOG[Google OAuth 2.0 API]
        RESEND_API[Resend Email Delivery]
    end

    subgraph Database ["Persistence Layer (PostgreSQL 16)"]
        USERS[(Users Table)]
        PRODUCTS[(Product Details Table)]
        HISTORY[(Price History Table)]
    end

    %% User Tracking Flow
    UI -->|1. Submit Product URL| API
    API --> TRACK_SVC
    TRACK_SVC -->|2. Scrape Metadata & Price| FC
    FC -->|3. Return Product Data| TRACK_SVC
    TRACK_SVC -->|4. Save Product & Initial Price| PRODUCTS
    TRACK_SVC -->|5. Insert History Record| HISTORY

    %% Scheduled Job Flow
    SCHED -->|Daily Cron 09:00 AM| TRACK_SVC
    TRACK_SVC -->|Fetch Latest Price| FC
    TRACK_SVC -->|Check Historical Min Price| HISTORY
    TRACK_SVC -->|If New Lowest Price| EMAIL_SVC
    EMAIL_SVC -->|Send Alert Email| RESEND_API
    RESEND_API -->|Deliver Notification| UI_USER[User Inbox]

    %% Auth Flow
    AUTH_UI -->|Google SSO / JWT| API
    API --> AUTH_SVC
    AUTH_SVC -->|Verify ID Token| GOOG
    AUTH_SVC -->|Manage Credentials & Tokens| USERS
```

---

## 🛠 Tech Stack

### Frontend
- **Framework**: [React 18](https://react.dev/) + [Vite 5](https://vitejs.dev/)
- **Charts & Visualization**: [Recharts](https://recharts.org/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Authentication**: [@react-oauth/google](https://www.npmjs.com/package/@react-oauth/google)
- **Styling**: CSS3 with CSS Custom Properties (Theme Variables)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **ORM & Database**: [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/) + [Asyncpg](https://github.com/MagicStack/asyncpg) + [Alembic](https://alembic.sqlalchemy.org/)
- **Task Scheduling**: [APScheduler (AsyncIOScheduler)](https://apscheduler.readthedocs.io/)
- **Web Scraping**: [Firecrawl Python SDK](https://github.com/mendableai/firecrawl)
- **Email Service**: [Resend Python SDK](https://resend.com/docs/api-reference/introduction)
- **Security & Tokens**: [PyJWT](https://pyjwt.readthedocs.io/), [pwdlib / Argon2](https://github.com/frankie567/pwdlib), [cryptography](https://cryptography.io/)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/) + [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

### Database & DevOps
- **Database**: [PostgreSQL 16 Alpine](https://hub.docker.com/_/postgres)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **Testing**: [Pytest](https://docs.pytest.org/) + [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) + [HTTPX](https://www.python-httpx.org/)
- **Continuous Integration**: [GitHub Actions](https://github.com/features/actions)

---

## 📂 Repository Structure

```text
Deal-Drop/
├── .github/
│   └── workflows/
│       └── ci.yml                     # GitHub Actions CI workflow
├── backend/                           # FastAPI backend service
│   ├── alembic/                       # Alembic database migration scripts
│   ├── app/
│   │   ├── core/                      # Application config, security & auth dependencies
│   │   │   ├── config.py              # Pydantic Settings configuration
│   │   │   ├── dependencies.py        # FastAPI auth dependencies
│   │   │   └── security.py            # Hashing & JWT token handlers
│   │   ├── db/                        # Async database engine and base model
│   │   ├── models/                    # SQLAlchemy database models (User, Product, PriceHistory)
│   │   ├── routes/                    # API route controllers (Auth, Products)
│   │   ├── schemas/                   # Pydantic request & response schemas
│   │   ├── services/                  # Business logic services (Firecrawl, Scheduler, Email, OAuth)
│   │   │   ├── email_service.py       # Resend transactional email handler
│   │   │   ├── firecrawl_service.py   # Firecrawl web scraping integration
│   │   │   ├── google_auth_service.py # Google OAuth token verification
│   │   │   ├── price_tracker_service.py # Price comparison & lowest price engine
│   │   │   └── scheduler_service.py   # APScheduler cron job scheduler
│   │   ├── utils/                     # Utility helpers (currency normalizer)
│   │   └── main.py                    # FastAPI application entrypoint & lifespan
│   ├── tests/                         # Pytest test suite for backend services and endpoints
│   ├── Dockerfile                     # Production backend Docker image definition
│   ├── pytest.ini                     # Pytest configuration
│   ├── requirements.txt               # Backend Python dependencies
│   └── README.md                      # Dedicated backend setup guide
├── frontend/                          # React + Vite frontend application
│   ├── public/                        # Static assets (favicons, SVGs)
│   ├── src/
│   │   ├── api/                       # API client with authorization header interceptors
│   │   ├── components/                # Modular React components
│   │   │   ├── AuthModal.jsx          # Sign In / Sign Up / Forgot Password Modal
│   │   │   ├── FeatureSection.jsx     # Landing feature showcase
│   │   │   ├── Footer.jsx             # Footer component
│   │   │   ├── Header.jsx             # Header navbar with theme toggle & user menu
│   │   │   ├── Hero.jsx               # Hero section with URL input for product tracking
│   │   │   ├── ProfileDropdown.jsx    # User profile & account dropdown
│   │   │   ├── ResetPassword.jsx      # Password reset page
│   │   │   └── TrackedProducts.jsx    # Tracked items grid & interactive Recharts view
│   │   ├── App.jsx                    # Root React component with theme & session state
│   │   ├── App.css                    # Design system and CSS custom properties
│   │   └── main.jsx                   # React DOM render entry point
│   ├── Dockerfile                     # Frontend Docker image definition
│   ├── package.json                   # Frontend dependencies and npm scripts
│   ├── vite.config.js                 # Vite bundler configuration
│   └── README.md                      # Dedicated frontend setup guide
├── docker-compose.yml                 # Multi-container orchestration (DB, Backend, Frontend)
└── README.md                          # Main repository documentation
```

---

## 📡 API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Register a new user with email and password | No |
| `POST` | `/auth/login` | Authenticate with credentials and receive JWT token | No |
| `POST` | `/auth/google` | Authenticate using Google OAuth 2.0 credential token | No |
| `POST` | `/auth/forgot-password` | Request a password reset email link | No |
| `POST` | `/auth/reset-password` | Reset password using one-time token | No |
| `GET` | `/auth/me` | Fetch authenticated user profile details | Bearer Token |

### Product & Price Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/products/track` | Scrape and register a new product URL for tracking | Bearer Token |
| `GET` | `/products/` | Retrieve all tracked products for the current user | Bearer Token |
| `GET` | `/products/{id}` | Get details of a specific tracked product | Bearer Token |
| `DELETE` | `/products/{id}` | Remove a product and its history from tracking | Bearer Token |
| `GET` | `/products/{id}/price-history` | Fetch chronological price history records for charts | Bearer Token |
| `POST` | `/products/{id}/check-price` | Manually trigger a price check for one product | Bearer Token |
| `POST` | `/products/check-all-prices` | Trigger price checks across all user's products | Bearer Token |

---

## ⚙️ Environment Configuration

### Backend Configuration (`backend/.env`)

Create a `.env` file in the `backend/` directory:

```env
# Database Settings
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/deal_drop
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dealdrop_test

# JWT Security
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Firecrawl Web Scraping API
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Resend Email Notification Service
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=DealDrop <onboarding@resend.dev>

# Google OAuth 2.0
GOOGLE_CLIENT_ID=your_google_oauth_client_id.apps.googleusercontent.com

# Frontend Application URL
FRONTEND_URL=http://localhost:5173
```

### Frontend Configuration (`frontend/.env`)

Create a `.env` file in the `frontend/` directory:

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Google OAuth Client ID
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id.apps.googleusercontent.com
```

---

## 🚀 Getting Started & Setup

### Option 1: Docker Compose (Quickstart)

Run the entire multi-container stack (PostgreSQL database, FastAPI backend, and React frontend) with a single command:

```bash
# Clone the repository
git clone https://github.com/BhargaviVyshnavi20/Deal-Drop.git
cd Deal-Drop

# Start all services
docker compose up --build
```

Access the applications:
- **Frontend UI**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database**: `localhost:5432`

---

### Option 2: Modular Local Setup

For individual component development, refer to each module's dedicated setup guide:

#### 🔹 Backend Setup
For detailed Python environment setup, virtual environments, dependencies, and database migrations:
👉 **[Backend Setup & Documentation](backend/README.md)**

```bash
cd backend
python -m venv env
# Windows: .\env\Scripts\activate | Linux/macOS: source env/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### 🔹 Frontend Setup
For Node.js configuration, npm packages, environment variables, and Vite dev server:
👉 **[Frontend Setup & Documentation](frontend/README.md)**

```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Testing & CI/CD

DealDrop includes automated Pytest suites covering unit tests, authentication, database isolation, scraping workflows, and background scheduler services.

### Running Backend Tests Locally

```bash
cd backend
pytest
```

To run a specific test suite:
```bash
# Test authentication flow
pytest tests/test_auth.py

# Test product tracker & price drop alert logic
pytest tests/test_price_tracker_service.py

# Test Firecrawl scraping service
pytest tests/test_firecrawl_service.py

# Test email notifications
pytest tests/test_email_service.py
```

### CI/CD Pipeline (`.github/workflows/ci.yml`)

Every pull request and push to the `main` branch triggers the GitHub Actions CI pipeline:
1. **Backend Tests Job**: Spawns a PostgreSQL service container, installs dependencies, and runs `pytest`.
2. **Frontend Build Job**: Sets up Node.js 22, installs dependencies via `npm ci`, and validates the production bundle build (`npm run build`).
3. **Docker Build Job**: Validates that both backend and frontend Docker containers build cleanly without errors.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
