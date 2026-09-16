# Frontend Setup

## Prerequisites

Make sure the following are installed:

- Node.js 18+
- npm
- Git

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd DealDrop/frontend
```

---

## 2. Install Dependencies

```bash
npm install
```

---

## 3. Configure Environment Variables

Create a `.env` file inside the `frontend` directory.

Add the backend API URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

For production, replace the URL with the deployed backend API URL.

Use the exact variable name expected by the frontend configuration.

> **Important:** Do not store private API keys, secrets, or credentials in frontend environment variables.

---

## 4. Start the Development Server

Run the following command:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

Open the URL in your browser.

---

## 5. Build for Production

Create the production build:

```bash
npm run build
```

The production files will be generated in:

```text
dist/
```

---

## 6. Preview the Production Build

To preview the production build locally:

```bash
npm run preview
```

---

## 7. Verify the Setup

Make sure:

- The frontend loads at `http://localhost:5173`
- The backend is running at `http://localhost:8000`
- The frontend can communicate with the configured backend API

---

## Docker

If you prefer to run the frontend using Docker, build the image:

```bash
docker build -t dealdrop-frontend .
```

Then run the container:

```bash
docker run -p 5173:5173 dealdrop-frontend
```

> If the `Dockerfile` exposes a different port, use that port instead.
