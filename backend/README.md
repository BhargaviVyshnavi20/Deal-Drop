# Backend Setup

## Prerequisites

Make sure the following are installed:

- Python 3.10+
- PostgreSQL
- Git

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd DealDrop/backend
```

---

## 2. Create and Activate a Virtual Environment

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file inside the `backend` directory.

Add the required environment variables:

```env
DATABASE_URL=<postgresql-connection-string>
SECRET_KEY=<your-secret-key>

FIRECRAWL_API_KEY=<your-firecrawl-api-key>

RESEND_API_KEY=<your-resend-api-key>
FROM_EMAIL=<your-verified-sender-email>

FRONTEND_URL=http://localhost:5173
```

Use the exact variable names expected by the backend configuration.

> **Important:** Never commit `.env` files or secrets to Git.

---

## 5. Set Up the Database

Create the PostgreSQL database configured in `DATABASE_URL`.

Then apply the existing database migrations:

```bash
alembic upgrade head
```

---

## 6. Start the Backend

Run the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

> If the FastAPI entry point differs from `app.main:app`, use the module defined by the project.

---

## 7. Verify the Setup

Open the API documentation in your browser:

```text
http://localhost:8000/docs
```

If the Swagger UI loads successfully, the backend is running correctly.

---

## Docker

If you prefer to run the backend using Docker, build the image:

```bash
docker build -t dealdrop-backend .
```

Then run the container:

```bash
docker run -p 8000:8000 --env-file .env dealdrop-backend
```

The backend will be available at:

```text
http://localhost:8000
```
