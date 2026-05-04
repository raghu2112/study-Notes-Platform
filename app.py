"""
=============================================================
  StudyNotes Platform — Flask Backend
  app.py | Main application entry point
  Tech: Flask + SQLite + Session Auth
=============================================================
"""

import os
import re
import math
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, g, request, session, redirect, url_for,
    render_template, flash, abort, send_from_directory, jsonify
)
from werkzeug.utils import secure_filename

# ─────────────────────────────────────────────
#  APP CONFIGURATION
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Secure random secret key

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATABASE     = os.path.join(BASE_DIR, 'studynotes.db')
UPLOAD_DIR   = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXT  = {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'png', 'jpg'}
MAX_MB       = 20
PER_PAGE     = 9   # Notes per page

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = MAX_MB * 1024 * 1024  # 20 MB limit


# ─────────────────────────────────────────────
#  DATABASE HELPERS
# ─────────────────────────────────────────────
def get_db():
    """Return a database connection for this request context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row   # dict-style rows
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode = WAL")
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()


def query(sql, args=(), one=False):
    """Execute a SELECT and return rows."""
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    """Execute INSERT / UPDATE / DELETE, commit, and return lastrowid."""
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


def init_db():
    """Create all tables and insert seed data (runs once)."""
    db = get_db()
    db.executescript(open(os.path.join(BASE_DIR, 'schema.sql')).read())
    db.commit()

    # Seed admin account if not present
    admin = query("SELECT id FROM users WHERE email = ?", ('admin@studynotes.com',), one=True)
    if not admin:
        ph = hash_password('Admin@123')
        db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
            ('Admin User', 'admin@studynotes.com', ph, 'admin')
        )

    # Seed sample student
    stu = query("SELECT id FROM users WHERE email = ?", ('demo@student.com',), one=True)
    if not stu:
        ph = hash_password('Demo@123')
        db.execute(
            "INSERT INTO users (name, email, password_hash, role, bio) VALUES (?,?,?,?,?)",
            ('Demo Student', 'demo@student.com', ph, 'student',
             'B.Tech 3rd Year | Loves DSA and Machine Learning')
        )

    db.commit()


# ─────────────────────────────────────────────
#  SECURITY HELPERS
# ─────────────────────────────────────────────
def hash_password(password):
    """SHA-256 hash with random salt."""
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def check_password(stored, entered):
    """Verify a password against a stored salted hash."""
    try:
        salt, h = stored.split(':', 1)
        return hashlib.sha256((salt + entered).encode()).hexdigest() == h
    except Exception:
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def sanitize(text):
    """Strip dangerous HTML characters from user input."""
    return re.sub(r'[<>"\'`]', '', str(text).strip()) if text else ''


# ─────────────────────────────────────────────
#  AUTH DECORATORS
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to continue.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
#  CONTEXT PROCESSORS & FILTERS
# ─────────────────────────────────────────────
@app.context_processor
def inject_globals():
    """Make current_user and helpers available in all templates."""
    user = None
    if 'user_id' in session:
        user = query("SELECT * FROM users WHERE id = ?", (session['user_id'],), one=True)
    notif_count = 0
    if user:
        notif_count = query(
            "SELECT COUNT(*) as c FROM notifications WHERE user_id=? AND read=0",
            (user['id'],), one=True
        )['c']
    return dict(current_user=user, notif_count=notif_count)


@app.template_filter('timeago')
def timeago_filter(dt_str):
    """Convert ISO datetime string to human-readable 'X ago' format."""
    try:
        dt = datetime.fromisoformat(str(dt_str))
        diff = datetime.utcnow() - dt
        s = diff.total_seconds()
        if s < 60:       return 'just now'
        if s < 3600:     return f"{int(s//60)}m ago"
        if s < 86400:    return f"{int(s//3600)}h ago"
        if s < 2592000:  return f"{int(s//86400)}d ago"
        return dt.strftime('%d %b %Y')
    except Exception:
        return str(dt_str)


@app.template_filter('fileicon')
def fileicon_filter(ext):
    icons = {'pdf': '📄', 'doc': '📝', 'docx': '📝', 'txt': '📃',
             'ppt': '📊', 'pptx': '📊', 'png': '🖼️', 'jpg': '🖼️'}
    return icons.get(str(ext).lower(), '📎')


# ─────────────────────────────────────────────
#  ROUTES — PUBLIC
# ─────────────────────────────────────────────

@app.route('/')
def index():
    """Home page — shows stats + recent/trending notes."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    stats = {
        'notes':    query("SELECT COUNT(*) as c FROM notes", one=True)['c'],
        'users':    query("SELECT COUNT(*) as c FROM users", one=True)['c'],
        'comments': query("SELECT COUNT(*) as c FROM comments", one=True)['c'],
        'views':    query("SELECT COALESCE(SUM(views),0) as c FROM notes", one=True)['c'],
    }
    recent   = query("SELECT n.*, u.name as author_name FROM notes n "
                     "JOIN users u ON n.user_id=u.id "
                     "WHERE n.is_deleted=0 ORDER BY n.created_at DESC LIMIT 6")
    trending = query("SELECT n.*, u.name as author_name FROM notes n "
                     "JOIN users u ON n.user_id=u.id "
                     "WHERE n.is_deleted=0 ORDER BY (n.views + n.likes*2) DESC LIMIT 5")
    return render_template('index.html', stats=stats, recent=recent, trending=trending)


# ─────────────────────────────────────────────
#  ROUTES — AUTH
# ─────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('notes'))

    if request.method == 'POST':
        name     = sanitize(request.form.get('name', ''))
        email    = sanitize(request.form.get('email', ''))
        password = request.form.get('password', '')
        role     = request.form.get('role', 'student')

        # Validation
        errors = []
        if len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not re.match(r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Enter a valid email address.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one digit.')
        if role not in ('student', 'admin'):
            role = 'student'

        if query("SELECT id FROM users WHERE email=?", (email,), one=True):
            errors.append('An account with this email already exists.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('register.html', form=request.form)

        uid = execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
            (name, email, hash_password(password), role)
        )
        session.clear()
        session['user_id'] = uid
        session['role']    = role
        session.permanent  = True
        flash(f'Welcome, {name}! Your account has been created. 🎉', 'success')
        return redirect(url_for('notes'))

    return render_template('register.html', form={})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('notes'))

    if request.method == 'POST':
        email    = sanitize(request.form.get('email', ''))
        password = request.form.get('password', '')
        next_url = request.form.get('next', url_for('notes'))

        user = query("SELECT * FROM users WHERE email=?", (email,), one=True)
        if not user or not check_password(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html', form=request.form)

        if user['is_blocked']:
            flash('Your account has been suspended. Contact admin.', 'error')
            return render_template('login.html', form=request.form)

        session.clear()
        session['user_id']   = user['id']
        session['role']      = user['role']
        session.permanent    = True

        # Update last_login
        execute("UPDATE users SET last_login=? WHERE id=?",
                (datetime.utcnow().isoformat(), user['id']))

        flash(f'Welcome back, {user["name"]}! 👋', 'success')
        return redirect(next_url if next_url.startswith('/') else url_for('notes'))

    return render_template('login.html', form={}, next=request.args.get('next', ''))


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('index'))


# ─────────────────────────────────────────────
#  ROUTES — NOTES
# ─────────────────────────────────────────────

@app.route('/notes')
def notes():
    """Browse all notes with search, filter, and pagination."""
    q       = sanitize(request.args.get('q', ''))
    subject = sanitize(request.args.get('subject', ''))
    sort    = request.args.get('sort', 'recent')
    page    = max(1, int(request.args.get('page', 1)))

    base_sql = ("SELECT n.*, u.name as author_name, "
                "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating, "
                "(SELECT COUNT(*) FROM ratings WHERE note_id=n.id) as rating_count, "
                "(SELECT COUNT(*) FROM comments WHERE note_id=n.id AND is_deleted=0) as comment_count "
                "FROM notes n JOIN users u ON n.user_id=u.id "
                "WHERE n.is_deleted=0 ")
    args = []

    if q:
        base_sql += "AND (n.title LIKE ? OR n.description LIKE ? OR n.tags LIKE ? OR u.name LIKE ?) "
        like = f'%{q}%'
        args += [like, like, like, like]
    if subject:
        base_sql += "AND n.subject=? "
        args.append(subject)

    sort_map = {
        'recent':  'n.created_at DESC',
        'popular': 'n.likes DESC',
        'rating':  'avg_rating DESC',
        'views':   'n.views DESC',
    }
    base_sql += f"ORDER BY {sort_map.get(sort,'n.created_at DESC')} "

    # Count total for pagination
    count_sql = base_sql.replace(
        "SELECT n.*, u.name as author_name, "
        "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating, "
        "(SELECT COUNT(*) FROM ratings WHERE note_id=n.id) as rating_count, "
        "(SELECT COUNT(*) FROM comments WHERE note_id=n.id AND is_deleted=0) as comment_count ",
        "SELECT COUNT(*) as c "
    ).split("ORDER BY")[0]
    total = get_db().execute(count_sql, args).fetchone()['c']
    total_pages = max(1, math.ceil(total / PER_PAGE))
    page = min(page, total_pages)

    base_sql += f"LIMIT {PER_PAGE} OFFSET {(page-1)*PER_PAGE}"
    note_list = query(base_sql, args)

    subjects = [r['subject'] for r in query("SELECT DISTINCT subject FROM notes WHERE is_deleted=0 AND subject!='' ORDER BY subject")]

    # Get user liked note IDs for UI state
    liked_ids = set()
    if 'user_id' in session:
        rows = query("SELECT note_id FROM likes WHERE user_id=?", (session['user_id'],))
        liked_ids = {r['note_id'] for r in rows}

    return render_template('notes.html',
        notes=note_list, q=q, subject=subject, sort=sort,
        subjects=subjects, page=page, total_pages=total_pages,
        total=total, liked_ids=liked_ids)


@app.route('/note/<int:note_id>')
def note_detail(note_id):
    """View a single note with comments and ratings."""
    note = query(
        "SELECT n.*, u.name as author_name, u.avatar as author_avatar, "
        "u.bio as author_bio, "
        "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating, "
        "(SELECT COUNT(*) FROM ratings WHERE note_id=n.id) as rating_count "
        "FROM notes n JOIN users u ON n.user_id=u.id "
        "WHERE n.id=? AND n.is_deleted=0",
        (note_id,), one=True
    )
    if not note:
        abort(404)

    # Increment view count (simple; no dedup for demo)
    execute("UPDATE notes SET views=views+1 WHERE id=?", (note_id,))

    comments = query(
        "SELECT c.*, u.name as user_name, u.avatar as user_avatar "
        "FROM comments c JOIN users u ON c.user_id=u.id "
        "WHERE c.note_id=? AND c.is_deleted=0 ORDER BY c.created_at DESC",
        (note_id,)
    )

    user_rating = None
    user_liked  = False
    user_bookmarked = False
    if 'user_id' in session:
        uid = session['user_id']
        r = query("SELECT stars FROM ratings WHERE note_id=? AND user_id=?", (note_id, uid), one=True)
        if r:
            user_rating = r['stars']
        lk = query("SELECT 1 FROM likes WHERE note_id=? AND user_id=?", (note_id, uid), one=True)
        user_liked = bool(lk)
        bk = query("SELECT 1 FROM bookmarks WHERE note_id=? AND user_id=?", (note_id, uid), one=True)
        user_bookmarked = bool(bk)

    # Related notes (same subject)
    related = query(
        "SELECT n.id, n.title, n.file_type FROM notes n "
        "WHERE n.subject=? AND n.id!=? AND n.is_deleted=0 LIMIT 4",
        (note['subject'], note_id)
    )

    return render_template('note_detail.html',
        note=note, comments=comments, user_rating=user_rating,
        user_liked=user_liked, user_bookmarked=user_bookmarked,
        related=related)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload a new study note."""
    if request.method == 'POST':
        title    = sanitize(request.form.get('title', ''))
        subject  = sanitize(request.form.get('subject', ''))
        desc     = sanitize(request.form.get('description', ''))
        tags_raw = sanitize(request.form.get('tags', ''))
        tags     = ','.join([t.strip() for t in tags_raw.split(',') if t.strip()])

        errors = []
        if not title:
            errors.append('Note title is required.')
        if not subject:
            errors.append('Subject is required.')

        file = request.files.get('file')
        filename = file_size = file_type = None

        if file and file.filename:
            if not allowed_file(file.filename):
                errors.append(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXT)}')
            else:
                filename  = secure_filename(
                    f"{session['user_id']}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
                )
                file_type = filename.rsplit('.', 1)[1].lower()
                # Check size via content-length header (backup)
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                if file_size > MAX_MB * 1024 * 1024:
                    errors.append(f'File too large. Max {MAX_MB} MB allowed.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('upload.html', form=request.form)

        if filename:
            file.save(os.path.join(UPLOAD_DIR, filename))

        note_id = execute(
            "INSERT INTO notes (user_id, title, subject, description, tags, "
            "filename, file_type, file_size) VALUES (?,?,?,?,?,?,?,?)",
            (session['user_id'], title, subject, desc, tags,
             filename, file_type, file_size)
        )

        # Create notification for followers (demo: just for admin)
        execute(
            "INSERT INTO notifications (user_id, type, message, link) VALUES (?,?,?,?)",
            (session['user_id'], 'upload',
             f'You uploaded "{title}" successfully.',
             f'/note/{note_id}')
        )

        flash('Note uploaded successfully! 🎉', 'success')
        return redirect(url_for('note_detail', note_id=note_id))

    return render_template('upload.html', form={})


@app.route('/note/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = query("SELECT * FROM notes WHERE id=? AND is_deleted=0", (note_id,), one=True)
    if not note:
        abort(404)
    # Only author or admin can delete
    if note['user_id'] != session['user_id'] and session.get('role') != 'admin':
        abort(403)

    execute("UPDATE notes SET is_deleted=1 WHERE id=?", (note_id,))
    # Delete physical file
    if note['filename']:
        fp = os.path.join(UPLOAD_DIR, note['filename'])
        if os.path.exists(fp):
            os.remove(fp)

    flash('Note deleted.', 'success')
    return redirect(url_for('notes'))


@app.route('/download/<int:note_id>')
def download_note(note_id):
    note = query("SELECT * FROM notes WHERE id=? AND is_deleted=0", (note_id,), one=True)
    if not note or not note['filename']:
        abort(404)
    execute("UPDATE notes SET downloads=downloads+1 WHERE id=?", (note_id,))
    return send_from_directory(UPLOAD_DIR, note['filename'],
                               as_attachment=True,
                               download_name=note['title'] + '.' + (note['file_type'] or 'bin'))


# ─────────────────────────────────────────────
#  HELPER — detect AJAX requests
# ─────────────────────────────────────────────
def _is_ajax():
    """Return True when the request is an AJAX / fetch call."""
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or request.content_type == 'application/json'
        or request.accept_mimetypes.best == 'application/json'
    )


# ─────────────────────────────────────────────
#  ROUTES — INTERACTIONS (AJAX + Forms)
# ─────────────────────────────────────────────

@app.route('/note/<int:note_id>/like', methods=['POST'])
@login_required
def toggle_like(note_id):
    uid = session['user_id']
    existing = query("SELECT 1 FROM likes WHERE note_id=? AND user_id=?", (note_id, uid), one=True)
    if existing:
        execute("DELETE FROM likes WHERE note_id=? AND user_id=?", (note_id, uid))
        execute("UPDATE notes SET likes=MAX(0,likes-1) WHERE id=?", (note_id,))
        liked = False
    else:
        execute("INSERT OR IGNORE INTO likes (note_id, user_id) VALUES (?,?)", (note_id, uid))
        execute("UPDATE notes SET likes=likes+1 WHERE id=?", (note_id,))
        liked = True
        # Notify author
        note = query("SELECT user_id, title FROM notes WHERE id=?", (note_id,), one=True)
        if note and note['user_id'] != uid:
            user = query("SELECT name FROM users WHERE id=?", (uid,), one=True)
            execute("INSERT INTO notifications (user_id,type,message,link) VALUES (?,?,?,?)",
                    (note['user_id'], 'like',
                     f'{user["name"]} liked your note "{note["title"]}".',
                     f'/note/{note_id}'))

    count = query("SELECT likes FROM notes WHERE id=?", (note_id,), one=True)['likes']
    if _is_ajax():
        return jsonify({'liked': liked, 'count': count})
    return redirect(url_for('note_detail', note_id=note_id))


@app.route('/note/<int:note_id>/rate', methods=['POST'])
@login_required
def rate_note(note_id):
    uid = session['user_id']
    # Accept JSON body or form data
    if request.is_json:
        stars = int(request.json.get('stars', 0))
    else:
        stars = int(request.form.get('stars', 0))
    if stars not in range(1, 6):
        if _is_ajax():
            return jsonify({'error': 'Rating must be between 1 and 5.'}), 400
        flash('Rating must be between 1 and 5.', 'error')
        return redirect(url_for('note_detail', note_id=note_id))

    execute("INSERT OR REPLACE INTO ratings (note_id, user_id, stars) VALUES (?,?,?)",
            (note_id, uid, stars))

    avg = query("SELECT COALESCE(AVG(stars),0) as avg, COUNT(*) as cnt FROM ratings WHERE note_id=?",
                (note_id,), one=True)
    if _is_ajax():
        return jsonify({
            'stars': stars,
            'avg_rating': round(float(avg['avg']), 1),
            'rating_count': avg['cnt']
        })
    flash(f'You rated this note {stars} ★', 'success')
    return redirect(url_for('note_detail', note_id=note_id))


@app.route('/note/<int:note_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(note_id):
    uid = session['user_id']
    ex = query("SELECT 1 FROM bookmarks WHERE note_id=? AND user_id=?", (note_id, uid), one=True)
    if ex:
        execute("DELETE FROM bookmarks WHERE note_id=? AND user_id=?", (note_id, uid))
        bookmarked = False
    else:
        execute("INSERT OR IGNORE INTO bookmarks (note_id, user_id) VALUES (?,?)", (note_id, uid))
        bookmarked = True
    if _is_ajax():
        return jsonify({'bookmarked': bookmarked})
    flash('Note bookmarked! 🔖' if bookmarked else 'Bookmark removed.', 'success')
    return redirect(url_for('note_detail', note_id=note_id))


@app.route('/note/<int:note_id>/comment', methods=['POST'])
@login_required
def add_comment(note_id):
    # Accept JSON body or form data
    if request.is_json:
        text = sanitize(request.json.get('text', ''))
    else:
        text = sanitize(request.form.get('text', ''))

    if len(text) < 2:
        if _is_ajax():
            return jsonify({'error': 'Comment cannot be empty.'}), 400
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('note_detail', note_id=note_id))
    if len(text) > 1000:
        if _is_ajax():
            return jsonify({'error': 'Comment too long (max 1000 characters).'}), 400
        flash('Comment too long (max 1000 characters).', 'error')
        return redirect(url_for('note_detail', note_id=note_id))

    cid = execute("INSERT INTO comments (note_id, user_id, text) VALUES (?,?,?)",
                  (note_id, session['user_id'], text))

    # Notify note author
    note = query("SELECT user_id, title FROM notes WHERE id=?", (note_id,), one=True)
    if note and note['user_id'] != session['user_id']:
        user = query("SELECT name FROM users WHERE id=?", (session['user_id'],), one=True)
        execute("INSERT INTO notifications (user_id,type,message,link) VALUES (?,?,?,?)",
                (note['user_id'], 'comment',
                 f'{user["name"]} commented on your note "{note["title"]}".',
                 f'/note/{note_id}'))

    if _is_ajax():
        me = query("SELECT name, avatar FROM users WHERE id=?", (session['user_id'],), one=True)
        total = query("SELECT COUNT(*) as c FROM comments WHERE note_id=? AND is_deleted=0",
                      (note_id,), one=True)['c']
        return jsonify({
            'id': cid,
            'text': text,
            'user_name': me['name'],
            'user_avatar': me['avatar'] or me['name'][:2].upper(),
            'created_at': 'just now',
            'can_delete': True,
            'total_comments': total
        })
    flash('Comment posted! 💬', 'success')
    return redirect(url_for('note_detail', note_id=note_id))


@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    c = query("SELECT * FROM comments WHERE id=?", (comment_id,), one=True)
    if not c:
        if _is_ajax():
            return jsonify({'error': 'Comment not found.'}), 404
        abort(404)
    if c['user_id'] != session['user_id'] and session.get('role') != 'admin':
        if _is_ajax():
            return jsonify({'error': 'Forbidden.'}), 403
        abort(403)
    execute("UPDATE comments SET is_deleted=1 WHERE id=?", (comment_id,))
    total = query("SELECT COUNT(*) as c FROM comments WHERE note_id=? AND is_deleted=0",
                  (c['note_id'],), one=True)['c']
    if _is_ajax():
        return jsonify({'deleted': True, 'comment_id': comment_id, 'total_comments': total})
    flash('Comment deleted.', 'success')
    return redirect(url_for('note_detail', note_id=c['note_id']))


# ─────────────────────────────────────────────
#  ROUTES — PROFILE & BOOKMARKS
# ─────────────────────────────────────────────

@app.route('/profile')
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id=None):
    if user_id is None:
        user_id = session['user_id']
    user = query("SELECT * FROM users WHERE id=?", (user_id,), one=True)
    if not user:
        abort(404)

    user_notes = query(
        "SELECT n.*, "
        "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating "
        "FROM notes n WHERE n.user_id=? AND n.is_deleted=0 ORDER BY n.created_at DESC",
        (user_id,)
    )
    total_views = sum(n['views'] for n in user_notes)
    total_likes = sum(n['likes'] for n in user_notes)

    return render_template('profile.html',
        profile_user=user, user_notes=user_notes,
        total_views=total_views, total_likes=total_likes)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    uid  = session['user_id']
    user = query("SELECT * FROM users WHERE id=?", (uid,), one=True)
    if request.method == 'POST':
        name = sanitize(request.form.get('name', ''))
        bio  = sanitize(request.form.get('bio', ''))
        if not name:
            flash('Name is required.', 'error')
            return render_template('edit_profile.html', user=user)
        execute("UPDATE users SET name=?, bio=? WHERE id=?", (name, bio, uid))
        flash('Profile updated! ✅', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)


@app.route('/bookmarks')
@login_required
def bookmarks():
    uid = session['user_id']
    bk_notes = query(
        "SELECT n.*, u.name as author_name, b.created_at as bookmarked_at "
        "FROM bookmarks b JOIN notes n ON b.note_id=n.id "
        "JOIN users u ON n.user_id=u.id "
        "WHERE b.user_id=? AND n.is_deleted=0 ORDER BY b.created_at DESC",
        (uid,)
    )
    return render_template('bookmarks.html', notes=bk_notes)


@app.route('/trending')
def trending():
    period = request.args.get('period', 'all')
    limit_date = datetime.utcnow()
    if period == 'week':
        limit_date -= timedelta(days=7)
    elif period == 'month':
        limit_date -= timedelta(days=30)
    else:
        limit_date = datetime(2000, 1, 1)

    sql = ("SELECT n.*, u.name as author_name, "
           "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating "
           "FROM notes n JOIN users u ON n.user_id=u.id "
           "WHERE n.is_deleted=0 AND n.created_at >= ? "
           "ORDER BY (n.views + n.likes*2) DESC LIMIT 15")
    note_list = query(sql, (limit_date.isoformat(),))
    return render_template('trending.html', notes=note_list, period=period)


@app.route('/my-notes')
@login_required
def my_notes():
    uid = session['user_id']
    user_notes = query(
        "SELECT n.*, "
        "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating, "
        "(SELECT COUNT(*) FROM ratings WHERE note_id=n.id) as rating_count, "
        "(SELECT COUNT(*) FROM comments WHERE note_id=n.id AND is_deleted=0) as comment_count "
        "FROM notes n WHERE n.user_id=? AND n.is_deleted=0 ORDER BY n.created_at DESC",
        (uid,)
    )
    # Aggregated stats for dashboard
    total_views = sum(n['views'] for n in user_notes)
    total_likes = sum(n['likes'] for n in user_notes)
    total_downloads = sum(n['downloads'] for n in user_notes)

    return render_template('my_notes.html', 
                         notes=user_notes,
                         total_views=total_views,
                         total_likes=total_likes, 
                         total_downloads=total_downloads)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pw = request.form.get('old_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')

        user = query("SELECT * FROM users WHERE id=?", (session['user_id'],), one=True)
        if not check_password(user['password_hash'], old_pw):
            flash('Current password is incorrect.', 'error')
        elif new_pw != confirm_pw:
            flash('New passwords do not match.', 'error')
        elif len(new_pw) < 8:
            flash('Password must be at least 8 characters.', 'error')
        else:
            execute("UPDATE users SET password_hash=? WHERE id=?",
                    (hash_password(new_pw), session['user_id']))
            flash('Password updated successfully! ✅', 'success')
            return redirect(url_for('profile'))

    return render_template('change_password.html')


@app.route('/tag/<tag>')
def browse_tag(tag):
    tag_clean = sanitize(tag)
    tag_notes = query(
        "SELECT n.*, u.name as author_name FROM notes n "
        "JOIN users u ON n.user_id=u.id "
        "WHERE n.is_deleted=0 AND n.tags LIKE ? ORDER BY n.created_at DESC",
        (f'%{tag_clean}%',)
    )
    return render_template('browse_tag.html', notes=tag_notes, tag=tag_clean)


# ─────────────────────────────────────────────
#  ROUTES — NOTIFICATIONS
# ─────────────────────────────────────────────

@app.route('/notifications')
@login_required
def notifications():
    uid = session['user_id']
    notifs = query("SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 50", (uid,))
    execute("UPDATE notifications SET read=1 WHERE user_id=?", (uid,))
    return render_template('notifications.html', notifications=notifs)


@app.route('/api/notifications/count')
@login_required
def api_notif_count():
    """AJAX endpoint — return unread notification count."""
    cnt = query("SELECT COUNT(*) as c FROM notifications WHERE user_id=? AND read=0",
                (session['user_id'],), one=True)['c']
    return jsonify({'count': cnt})


# ─────────────────────────────────────────────
#  ROUTES — AJAX API (Notes Search)
# ─────────────────────────────────────────────

@app.route('/api/notes')
def api_notes():
    """AJAX endpoint — return notes as JSON for live search/filter/pagination."""
    q       = sanitize(request.args.get('q', ''))
    subject = sanitize(request.args.get('subject', ''))
    sort    = request.args.get('sort', 'recent')
    page    = max(1, int(request.args.get('page', 1)))

    base_sql = ("SELECT n.*, u.name as author_name, "
                "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating, "
                "(SELECT COUNT(*) FROM ratings WHERE note_id=n.id) as rating_count, "
                "(SELECT COUNT(*) FROM comments WHERE note_id=n.id AND is_deleted=0) as comment_count "
                "FROM notes n JOIN users u ON n.user_id=u.id "
                "WHERE n.is_deleted=0 ")
    args = []

    if q:
        base_sql += "AND (n.title LIKE ? OR n.description LIKE ? OR n.tags LIKE ? OR u.name LIKE ?) "
        like = f'%{q}%'
        args += [like, like, like, like]
    if subject:
        base_sql += "AND n.subject=? "
        args.append(subject)

    sort_map = {
        'recent':  'n.created_at DESC',
        'popular': 'n.likes DESC',
        'rating':  'avg_rating DESC',
        'views':   'n.views DESC',
    }
    base_sql += f"ORDER BY {sort_map.get(sort,'n.created_at DESC')} "

    count_sql = base_sql.replace(
        "SELECT n.*, u.name as author_name, "
        "(SELECT COALESCE(AVG(stars),0) FROM ratings WHERE note_id=n.id) as avg_rating, "
        "(SELECT COUNT(*) FROM ratings WHERE note_id=n.id) as rating_count, "
        "(SELECT COUNT(*) FROM comments WHERE note_id=n.id AND is_deleted=0) as comment_count ",
        "SELECT COUNT(*) as c "
    ).split("ORDER BY")[0]
    total = get_db().execute(count_sql, args).fetchone()['c']
    total_pages = max(1, math.ceil(total / PER_PAGE))
    page = min(page, total_pages)

    base_sql += f"LIMIT {PER_PAGE} OFFSET {(page-1)*PER_PAGE}"
    rows = query(base_sql, args)

    liked_ids = set()
    if 'user_id' in session:
        lk = query("SELECT note_id FROM likes WHERE user_id=?", (session['user_id'],))
        liked_ids = {r['note_id'] for r in lk}

    notes_list = []
    for n in rows:
        notes_list.append({
            'id': n['id'],
            'title': n['title'],
            'description': n['description'] or 'No description available.',
            'subject': n['subject'] or '',
            'tags': n['tags'] or '',
            'file_type': n['file_type'] or 'txt',
            'views': n['views'],
            'likes': n['likes'],
            'downloads': n['downloads'],
            'avg_rating': round(float(n['avg_rating']), 1),
            'author_name': n['author_name'],
            'filename': n['filename'],
            'liked': n['id'] in liked_ids,
        })

    return jsonify({
        'notes': notes_list,
        'page': page,
        'total_pages': total_pages,
        'total': total
    })


# ─────────────────────────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'users':    query("SELECT COUNT(*) as c FROM users", one=True)['c'],
        'notes':    query("SELECT COUNT(*) as c FROM notes WHERE is_deleted=0", one=True)['c'],
        'comments': query("SELECT COUNT(*) as c FROM comments WHERE is_deleted=0", one=True)['c'],
        'blocked':  query("SELECT COUNT(*) as c FROM users WHERE is_blocked=1", one=True)['c'],
        'downloads':query("SELECT COALESCE(SUM(downloads),0) as c FROM notes", one=True)['c'],
        'views':    query("SELECT COALESCE(SUM(views),0) as c FROM notes", one=True)['c'],
    }
    users = query(
        "SELECT u.*, COUNT(n.id) as note_count FROM users u "
        "LEFT JOIN notes n ON n.user_id=u.id AND n.is_deleted=0 "
        "GROUP BY u.id ORDER BY u.created_at DESC"
    )
    all_notes = query(
        "SELECT n.*, u.name as author_name FROM notes n "
        "JOIN users u ON n.user_id=u.id "
        "WHERE n.is_deleted=0 ORDER BY n.created_at DESC"
    )
    return render_template('admin.html', stats=stats, users=users, all_notes=all_notes)


@app.route('/admin/user/<int:user_id>/block', methods=['POST'])
@login_required
@admin_required
def block_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot block yourself.', 'error')
        return redirect(url_for('admin_dashboard'))
    user = query("SELECT * FROM users WHERE id=?", (user_id,), one=True)
    if not user:
        abort(404)
    new_status = 0 if user['is_blocked'] else 1
    execute("UPDATE users SET is_blocked=? WHERE id=?", (new_status, user_id))
    action = 'blocked' if new_status else 'unblocked'
    flash(f'User {user["name"]} has been {action}.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete yourself.', 'error')
        return redirect(url_for('admin_dashboard'))
    # Soft delete all notes
    execute("UPDATE notes SET is_deleted=1 WHERE user_id=?", (user_id,))
    execute("DELETE FROM users WHERE id=?", (user_id,))
    flash('User and all their data removed.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/note/<int:note_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_note(note_id):
    note = query("SELECT * FROM notes WHERE id=?", (note_id,), one=True)
    if not note:
        abort(404)
    execute("UPDATE notes SET is_deleted=1 WHERE id=?", (note_id,))
    if note['filename']:
        fp = os.path.join(UPLOAD_DIR, note['filename'])
        if os.path.exists(fp):
            os.remove(fp)
    flash('Note removed.', 'success')
    return redirect(url_for('admin_dashboard'))


# ─────────────────────────────────────────────
#  ERROR HANDLERS
# ─────────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403,
        msg='You do not have permission to access this page.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404,
        msg='The page you were looking for does not exist.'), 404


@app.errorhandler(413)
def too_large(e):
    flash(f'File too large. Maximum allowed size is {MAX_MB} MB.', 'error')
    return redirect(url_for('upload'))


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500,
        msg='An internal server error occurred. Please try again.'), 500


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("\n" + "="*52)
    print("  StudyNotes Platform — Flask Server")
    print("="*52)
    print("  URL  : http://127.0.0.1:5000")
    print("  Admin: admin@studynotes.com / Admin@123")
    print("  Demo : demo@student.com   / Demo@123")
    print("="*52 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
