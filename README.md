# 🌿 Minimal Portfolio

A Python-first, minimalist personal portfolio website built with FastAPI.

## 🎯 Philosophy

> "Simplicity is the ultimate sophistication." — Leonardo da Vinci

This portfolio embraces:
- **Python-first architecture** — FastAPI backend with Jinja2 templates
- **Radical simplicity** — Every line of code serves a purpose
- **Calm aesthetics** — Typography, whitespace, and restraint
- **Zero-cost hosting** — Completely free to deploy and run

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  HTML + CSS + Minimal JS (Jinja2 Templates)             │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│   │  Routes  │──│ Services │──│  Models  │──│   Schemas    │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
│                              │                                   │
│   ┌──────────────────────────┴───────────────────────────────┐  │
│   │              Authentication (JWT)                         │  │
│   │         Only admin can Create/Update/Delete               │  │
│   └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database                               │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│   │   User   │  │   Post   │  │  Project │                      │
│   └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
portfolio/
├── app/
│   ├── __init__.py          # App factory
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration & environment
│   ├── database.py          # SQLite + SQLAlchemy setup
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py          # Admin user model
│   │   ├── post.py          # Blog post model
│   │   └── project.py       # Project model
│   │
│   ├── schemas/             # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   └── project.py
│   │
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT authentication
│   │   └── markdown.py      # Markdown rendering
│   │
│   ├── routes/              # API & page routes
│   │   ├── __init__.py
│   │   ├── pages.py         # Public page routes
│   │   ├── auth.py          # Login/logout routes
│   │   ├── admin.py         # Protected CRUD routes
│   │   └── api.py           # JSON API endpoints
│   │
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html        # Base layout
│   │   ├── components/      # Reusable components
│   │   │   ├── nav.html
│   │   │   ├── footer.html
│   │   │   └── post_card.html
│   │   └── pages/           # Page templates
│   │       ├── home.html
│   │       ├── about.html
│   │       ├── projects.html
│   │       ├── blog.html
│   │       ├── post.html
│   │       ├── contact.html
│   │       ├── login.html
│   │       └── admin/
│   │           ├── dashboard.html
│   │           └── editor.html
│   │
│   └── static/              # Static assets
│       ├── css/
│       │   └── style.css    # Minimal custom CSS
│       └── js/
│           └── main.js      # Minimal JavaScript
│
├── tests/                   # Test files
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🗃️ Database Schema

### User (Admin Only)
| Field          | Type     | Description                    |
|----------------|----------|--------------------------------|
| id             | Integer  | Primary key                    |
| username       | String   | Unique username                |
| hashed_password| String   | bcrypt hashed password         |
| created_at     | DateTime | Account creation timestamp     |

### Post (Blog)
| Field          | Type     | Description                    |
|----------------|----------|--------------------------------|
| id             | Integer  | Primary key                    |
| title          | String   | Post title                     |
| slug           | String   | URL-friendly identifier        |
| content        | Text     | Markdown content               |
| excerpt        | String   | Short preview text             |
| published      | Boolean  | Is visible to public?          |
| created_at     | DateTime | Creation timestamp             |
| updated_at     | DateTime | Last edit timestamp            |

### Project
| Field          | Type     | Description                    |
|----------------|----------|--------------------------------|
| id             | Integer  | Primary key                    |
| title          | String   | Project name                   |
| description    | Text     | Markdown description           |
| tech_stack     | String   | Comma-separated technologies   |
| url            | String   | Live project URL (optional)    |
| github_url     | String   | Repository URL (optional)      |
| featured       | Boolean  | Show on homepage?              |
| created_at     | DateTime | Creation timestamp             |

---

## 🔐 Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Admin visits /login                                       │
│           │                                                   │
│           ▼                                                   │
│  2. Submits username + password                               │
│           │                                                   │
│           ▼                                                   │
│  3. Server validates credentials                              │
│           │                                                   │
│     ┌─────┴─────┐                                            │
│     │           │                                            │
│  Invalid     Valid                                            │
│     │           │                                            │
│     ▼           ▼                                            │
│  Error      4. Create JWT token                               │
│  shown          │                                            │
│                 ▼                                            │
│           5. Set HTTP-only cookie                            │
│                 │                                            │
│                 ▼                                            │
│           6. Redirect to /admin                              │
│                 │                                            │
│                 ▼                                            │
│           7. Future requests include cookie                  │
│                 │                                            │
│                 ▼                                            │
│           8. Middleware validates JWT                        │
│                 │                                            │
│                 ▼                                            │
│           9. Access granted to protected routes              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Security Features:**
- JWT tokens with expiration
- HTTP-only cookies (prevents XSS)
- Password hashing with bcrypt
- Single admin user (no public registration)

---

## ✨ Unique Feature: Focus Mode

Press `Shift + F` anywhere on the site to toggle **Focus Mode**:
- Fades navigation and footer
- Centers content with breathing room
- Reduces visual noise for reading

This is implemented with ~30 lines of vanilla JavaScript, demonstrating that delightful interactions don't need heavy frameworks.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Local Development

```bash
# 1. Clone and enter directory
cd portfolio

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your settings

# 5. Initialize database with admin user
python -c "from app.database import init_db; init_db()"

# 6. Run development server
uvicorn app.main:app --reload

# 7. Open http://localhost:8000
```

---

## 🌐 Free Deployment Guide

### Option 1: Render (Recommended)

1. **Create account** at [render.com](https://render.com)

2. **Connect GitHub** repository

3. **Create Web Service**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   ```
   SECRET_KEY=your-secret-key-here
   ADMIN_USERNAME=your-username
   ADMIN_PASSWORD=your-secure-password
   DATABASE_URL=sqlite:///./portfolio.db
   ```

5. **Deploy** — Render auto-deploys on push

### Option 2: Fly.io

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`

2. Login: `fly auth login`

3. Create app: `fly launch`

4. Deploy: `fly deploy`

### Option 3: Railway

1. Visit [railway.app](https://railway.app)
2. Connect GitHub
3. Add environment variables
4. Deploy automatically

---

## 🎨 Design Philosophy

### Colors (3 max)
- **Primary**: `#1a1a2e` — Deep midnight blue
- **Accent**: `#e94560` — Warm coral
- **Background**: `#fafafa` — Soft white

### Typography
- **Headings**: Playfair Display — elegant serif
- **Body**: Source Sans Pro — clean sans-serif

### Spacing
- Generous whitespace
- Consistent rhythm (8px grid)
- Content max-width: 680px (optimal reading)

---

## 📚 Learning Resources

This project is designed to teach:

1. **FastAPI Basics**
   - Routes and path operations
   - Dependency injection
   - Request/response handling

2. **SQLAlchemy ORM**
   - Model definitions
   - Relationships
   - Queries and CRUD

3. **Jinja2 Templates**
   - Template inheritance
   - Filters and macros
   - Context passing

4. **JWT Authentication**
   - Token creation/validation
   - Cookie handling
   - Protected routes

5. **Clean Code Principles**
   - Separation of concerns
   - Single responsibility
   - Clear naming

---

## 🔮 Future Enhancements

- [ ] Image upload for posts
- [ ] RSS feed generation
- [ ] Reading time estimation
- [ ] View count analytics
- [ ] Tags and categories
- [ ] Search functionality
- [ ] Dark/light theme toggle
- [ ] Syntax highlighting for code

---

## 📄 License

MIT License — Use freely, learn deeply.

---

Built with 🌿 simplicity and Python.
