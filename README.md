# CourseHub

CourseHub is a full-stack web application that helps university students browse, search, and download academic documents: exams, TD, TP, courses, and corrections.

Resources are organized by **Speciality** and **Semester**, and grouped by **Professor** and **Document Type**. A secure **Admin Dashboard** lets administrators manage all platform content.

---

## Features

### Public Student Portal
- 3-step guided UI:
  1. Select a **Speciality** (e.g. Computer Science, Math)
  2. Choose a **Semester** (1-6)
  3. Browse the curated list of PDFs, filter by document type, or search by title, module, or professor
- Direct file downloads, no account required
- Download counter per document

### Admin Dashboard
- Secure, JWT-authenticated Single Page Application (SPA)
- Full CRUD on **Specialities**, **Modules**, **Professors**, and **Documents**
- Link and unlink Modules to Specialities
- Manage admin accounts and change your own password

### File Management
- PDF upload by the admin (PDF only)
- Automatic extraction of file metadata (size, MIME type)
- Physical file storage, and automatic deletion of the file when a document is removed

### Relational Data Model
- **Many-to-Many** between Specialities and Modules (via the `SpecialityModule` junction table)
- **Strict 1-to-1** between a Document and its Media (file) record

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy (ORM), Pydantic |
| Database | MySQL-compatible relational database |
| Frontend | Vanilla HTML5, CSS3, JavaScript (Fetch API) |
| Auth | JWT (python-jose), Passlib + Bcrypt |
| Tooling | uv / pip |

---

## Database Schema

| Entity | Description |
|---|---|
| `Admin` | Manages the system |
| `Speciality` | Academic fields (Math, CS, etc.) |
| `Module` | Academic subjects (e.g. Algebre 1) |
| `SpecialityModule` | Junction table linking Modules to Specialities |
| `Professor` | Authors of the documents |
| `Document` | Document metadata (title, semester, year, type) |
| `Media` | File metadata (filename, size, path) |

```
Speciality ──< SpecialityModule >── Module
                     │
                     └──< Document >── Professor
                              │
                              └── 1:1 ── Media
```

Document types: `exam_norm`, `exam_ratt`, `controle`, `td`, `tp`, `course`, `corrige`.

---

## Project Structure

```
.
├── api/
│   ├── admin/
│   │   ├── admins.py
│   │   ├── catalog.py
│   │   ├── documents.py
│   │   ├── professors.py
│   │   └── __init__.py
│   ├── auth.py
│   ├── middleware.py
│   ├── views.py
│   └── __init__.py
├── database/
│   ├── schemas/
│   ├── db_manager.py
│   └── models.py
├── front_end/
│   ├── dashboard.html
│   ├── index.html
│   └── login.html
├── config.py
├── create_admin.py
├── create_tables.py
├── drop_tables.py
├── main.py
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

---

## Getting Started

### Prerequisites
- Python 3.12
- A MySQL (or MySQL-compatible) database

### Installation

```bash
git clone https://github.com/redaoulhamri/coursehub.git
cd coursehub

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

If you use [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

### Configuration

The app reads its settings from `config.py` (database URL, JWT secret, and algorithm). **Set the environment variables to your own values** before running anything:

```env
DATABASE_URL=mysql+pymysql://user:password@host:3306/your_database
SECRET_KEY=a-long-random-secret
ALGO=HS256
```

Use your own database credentials and generate your own secret key. Never reuse the example values and never commit your `.env` file.

### Setup scripts

Run these from the project root, in this order:

| Script | What it does |
|---|---|
| `python create_tables.py` | Creates all the database tables. Run it once on a fresh database. |
| `python create_admin.py` | Creates the first admin account, so you can log in to the dashboard for the first time. |
| `python drop_tables.py` | Drops all the tables. **This deletes all your data**, use it only to reset the database. |

### Run the app

```bash
uvicorn main:app --reload
```

The API is served under the `/v1` prefix. The interactive docs (Swagger/ReDoc) are disabled by default.

---

## Hosting

CourseHub does not run on its own in production: you need to host it yourself.

- **Backend**: deploy the FastAPI app on a server or platform of your choice (a VPS, Railway, Render, etc.).
- **Database**: host a MySQL-compatible database and point `DATABASE_URL` to it.
- **Environment variables**: set `DATABASE_URL`, `SECRET_KEY`, and `ALGO` to your own values on the hosting platform.
- **Uploads**: uploaded PDFs are stored in the `uploads/` folder. Make sure your host keeps this folder persistent, or files will be lost on redeploy.
- **Frontend**: serve the `front_end/` files and make sure they call your deployed API URL.

---

## API Overview

All routes are prefixed with `/v1`.

### Public

| Method | Route | Description |
|---|---|---|
| GET | `/api/views/specialities` | List specialities |
| GET | `/api/views/specialities/{id}/modules` | List modules of a speciality |
| GET | `/api/views/documents` | List documents grouped by professor. Query: `speciality_id`, `semester`, `type`, `search` |
| GET | `/api/views/documents/{id}/download` | Get the file URL and increment the download count |

### Authentication

| Method | Route | Description |
|---|---|---|
| POST | `/api/auth/login` | Log in and receive a JWT. Supports `rememberme` for a longer session |

### Admin (JWT required)

Send the token in the header: `Authorization: Bearer <token>`

| Resource | Routes |
|---|---|
| Specialities | `/api/admin/catalog/specialities` (GET, POST, PUT, DELETE) |
| Modules | `/api/admin/catalog/modules` (GET, POST, PUT, DELETE) |
| Speciality-Modules | `/api/admin/catalog/speciality-modules` (GET, POST, DELETE) |
| Professors | `/api/admin/professors` (GET, POST, PUT, DELETE) |
| Documents | `/api/admin/documents` (GET, POST with PDF upload, PUT, DELETE) |
| Admins | `/api/admin/admins` (GET, POST, DELETE) and `/api/admin/admins/change-password` (PUT) |

---

## Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.

## Author

[@redaoulhamri](https://github.com/redaoulhamri)

