<img width="959" height="470" alt="Screenshot 2026-09-01 213144" src="https://github.com/user-attachments/assets/32653028-0d47-465b-a32a-a35edacb4d17" /># DealDrop

### Price Tracking & Price Alert Application

DealDrop is a full-stack price tracking application that allows users to track product prices, view price history, set target prices, and receive email alerts when prices drop.

## Tech Stack

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Firecrawl](https://img.shields.io/badge/Firecrawl-FF6B35?style=for-the-badge)
![Resend](https://img.shields.io/badge/Resend-000000?style=for-the-badge&logo=resend&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## Screenshots

### Landing Page

<img width="959" height="475" alt="image" src="https://github.com/user-attachments/assets/1b4ed88d-68fa-4ef2-9669-8a2aad3475a0" />


### Product Tracking

<img width="956" height="475" alt="image" src="https://github.com/user-attachments/assets/a25f7397-af57-4f3e-8390-912d62945d4c" />


### Price History
<img width="954" height="472" alt="image" src="https://github.com/user-attachments/assets/6ba58bc9-a152-464e-9fab-b9ce668be116" />


---

## Features

- User registration and login
- Google authentication
- Forgot password and password reset
- Add products using product URLs
- Automatic product data extraction
- Current price tracking
- Price history visualization
- Target price alerts
- Email notifications
- User-specific product tracking
- Dockerized frontend and backend

---

## How It Works

```text
User
  ↓
React Frontend
  ↓
FastAPI Backend
  ↓
Firecrawl → Product Data
  ↓
PostgreSQL → Product & Price History
  ↓
Price Monitoring
  ↓
Resend → Email Alert
```

---

## Project Structure

```text
Deal-Drop/
├── backend/
│   └── README.md
├── frontend/
│   └── README.md
├── docs/
│   └── screenshots/
└── README.md
```

---

## Setup

### Backend

See the [Backend Setup](backend/README.md).

### Frontend

See the [Frontend Setup](frontend/README.md).
