Backend Setup

Prerequisites

Python 3.10+

PostgreSQL

Git

1. Clone the Repository

git clone <repository-url>
cd DealDrop/backend

2. Create and Activate a Virtual Environment

Windows PowerShell

python -m venv venv
.\venv\Scripts\Activate.ps1

macOS / Linux

python3 -m venv venv
source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the backend directory.

Add the environment variables required by the backend, including the database, authentication, external API, and email configuration.

Example:

DATABASE_URL=<postgresql-connection-string>
SECRET_KEY=<your-secret-key>

FIRECRAWL_API_KEY=<your-firecrawl-api-key>

RESEND_API_KEY=<your-resend-api-key>
FROM_EMAIL=<your-verified-sender-email>

FRONTEND_URL=http://localhost:5173

Use the exact variable names expected by the backend configuration.

Never commit .env or secrets to Git.

5. Set Up the Database

Create the PostgreSQL database configured in DATABASE_URL.

Then apply the existing migrations:

alembic upgrade head

6. Start the Backend

uvicorn app.main:app --reload

The API will normally run at:

http://localhost:8000

API documentation:

http://localhost:8000/docs

If the project's FastAPI entry point differs from app.main:app, use the module defined by the project.

7. Verify the Setup

Open the API documentation at:

http://localhost:8000/docs

If it loads successfully, the backend is running.

Docker

If using Docker:

docker build -t dealdrop-backend .
docker run -p 8000:8000 --env-file .env dealdrop-backend
