# 📚 StudyNotes — Flask Full-Stack Application

A complete, production-ready collaborative study notes platform built with **Python Flask + SQLite**.

---

## 🚀 Quick Start (3 Steps)

### Step 1 — Install Dependencies
```bash
cd study-notes-flask
pip install flask werkzeug
```

### Step 2 — Run the Server
```bash
python app.py
```

### Step 3 — Open Your Browser
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Login Credentials

| Role    | Email                    | Password    |
|---------|--------------------------|-------------|
| **Admin**   | admin@studynotes.com | Admin@123   |
| **Student** | demo@student.com     | Demo@123    |

The **demo login buttons** on the login page fill credentials automatically.

---

## 📁 Project Structure

```
study-notes-flask/
│
├── app.py                  ← Main Flask backend (all routes + logic)
├── schema.sql              ← SQLite schema (auto-runs on first start)
├── requirements.txt        ← Python dependencies
├── studynotes.db           ← SQLite database (auto-created)
├── uploads/                ← Uploaded files (auto-created)
│
└── templates/              ← Jinja2 HTML templates (internal CSS)
    ├── base.html           ← Master layout: sidebar + header + styles
    ├── index.html          ← Dashboard with stats + trending
    ├── login.html          ← Login form with demo shortcuts
    ├── register.html       ← Registration with validation
    ├── notes.html          ← Browse + search + filter + paginate
    ├── note_detail.html    ← Note view, comments, rating, actions
    ├── upload.html         ← Upload form with drag-and-drop
    ├── profile.html        ← User profile + uploaded notes
    ├── edit_profile.html   ← Edit name/bio
    ├── bookmarks.html      ← Saved notes
    ├── notifications.html  ← Activity notifications
    ├── admin.html          ← Admin panel: users + notes
    └── error.html          ← 403 / 404 / 500 error pages
```

---

## 🗄️ Database Schema (SQLite)

```sql
users        (id, name, email, password_hash, role, bio, is_blocked, last_login, created_at)
notes        (id, user_id, title, subject, description, tags, filename, file_type, file_size, views, likes, downloads, is_deleted, created_at)
comments     (id, note_id, user_id, text, is_deleted, created_at)
ratings      (id, note_id, user_id, stars, created_at) -- UNIQUE per user per note
likes        (id, note_id, user_id, created_at)        -- UNIQUE per user per note
bookmarks    (id, note_id, user_id, created_at)        -- UNIQUE per user per note
notifications(id, user_id, type, message, link, read, created_at)
```

---

## 🌐 All Backend Routes

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET/POST | `/` | ✅ | Dashboard with stats, trending, recent |
| GET/POST | `/register` | ❌ | User registration |
| GET/POST | `/login` | ❌ | User login |
| GET | `/logout` | ✅ | Session logout |
| GET/POST | `/upload` | ✅ | Upload study note |
| GET | `/notes` | ❌ | Browse + search + filter + paginate |
| GET | `/note/<id>` | ❌ | Note detail: comments, rating, actions |
| POST | `/note/<id>/delete` | ✅ | Delete note (author/admin) |
| GET | `/download/<id>` | ❌ | Download note file |
| POST | `/note/<id>/like` | ✅ | Toggle like/unlike |
| POST | `/note/<id>/rate` | ✅ | Submit star rating |
| POST | `/note/<id>/bookmark` | ✅ | Toggle bookmark |
| POST | `/note/<id>/comment` | ✅ | Add comment |
| POST | `/comment/<id>/delete` | ✅ | Delete comment (owner/admin) |
| GET | `/profile` | ✅ | View own profile |
| GET | `/profile/<id>` | ✅ | View another user's profile |
| GET/POST | `/profile/edit` | ✅ | Edit name/bio |
| GET | `/bookmarks` | ✅ | Saved notes |
| GET | `/notifications` | ✅ | Activity feed |
| GET | `/admin` | 👑 | Admin dashboard |
| POST | `/admin/user/<id>/block` | 👑 | Block/unblock user |
| POST | `/admin/user/<id>/delete` | 👑 | Delete user |
| POST | `/admin/note/<id>/delete` | 👑 | Force-delete note |

---

## ⚙️ How Frontend Connects to Backend

```
Browser → HTML Form (POST) → Flask Route → SQLite → Redirect/Template
```

Every interactive action uses standard HTML forms with `method="post"`:
- **Login/Register**: form POST → Flask validates → session cookie → redirect
- **Upload**: `enctype="multipart/form-data"` → `werkzeug.secure_filename` → saves to `/uploads`
- **Like/Bookmark**: form POST → toggles DB record → redirect back
- **Comments**: form POST → INSERT to DB → redirect with flash message
- **Search/Filter**: GET query params → SQL WHERE clauses → paginated results

JavaScript is used **only for UX enhancements**:
- Form validation (client-side duplicate of server validation)
- File drag-and-drop zone
- Upload progress bar animation
- Star rating hover effects
- Admin table live search filter
- Auto-dismiss flash messages

---

## 🔐 Security Features

| Feature | Implementation |
|---------|---------------|
| Password hashing | SHA-256 + random 16-byte salt |
| Session security | `secrets.token_hex(32)` as secret key |
| Input sanitization | `sanitize()` strips `<>"'\`` from all user input |
| File upload safety | `werkzeug.secure_filename` + whitelist extension check |
| File size limit | 20 MB via `MAX_CONTENT_LENGTH` |
| Auth decorators | `@login_required`, `@admin_required` on all protected routes |
| Foreign key protection | `PRAGMA foreign_keys = ON` in SQLite |
| Soft deletes | Notes/comments soft-deleted (not destroyed immediately) |
| CSRF baseline | Session-based forms (add Flask-WTF for full CSRF tokens) |
| Blocked user check | Login rejects blocked accounts |

---

## 🔮 Future Improvements

- **Flask-WTF** for CSRF protection on all forms
- **Flask-Login** for more robust session management
- **Real file preview** using PDF.js inline viewer
- **WebSockets** for real-time notifications (Flask-SocketIO)
- **Full-text search** using SQLite FTS5 virtual tables
- **Email verification** via Flask-Mail
- **Rate limiting** with Flask-Limiter
- **REST API** endpoints for mobile app integration
- **Docker** containerization for easy deployment
- **PostgreSQL** migration for production scale

---

*Built with Python Flask + SQLite + Jinja2 | No external CSS frameworks*
