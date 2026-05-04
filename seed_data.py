"""
seed_data.py — Populate the database with rich demo data.
Run ONCE after first launch:  python seed_data.py
"""

import sqlite3, hashlib, secrets, os
from datetime import datetime, timedelta

DB = os.path.join(os.path.dirname(__file__), 'studynotes.db')


def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def ts(days_ago=0, hours_ago=0):
    dt = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def run():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    cur = con.cursor()

    # ── Extra Users ──────────────────────────────────────────
    extra_users = [
        ('Arjun Mehta',    'arjun@student.com',  'Student@1', 'student',
         'B.Tech CSE 3rd year | Loves DSA and competitive programming.'),
        ('Priya Sharma',   'priya@student.com',  'Student@2', 'student',
         'ECE enthusiast | Note-taker extraordinaire.'),
        ('Rohan Das',      'rohan@student.com',  'Student@3', 'student',
         '2nd year AIML | Python and TensorFlow aficionado.'),
        ('Sneha Iyer',     'sneha@student.com',  'Student@4', 'student',
         'Civil Engineering student | Loves maths.'),
    ]
    uid_map = {}
    for name, email, pwd, role, bio in extra_users:
        ex = con.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if ex:
            uid_map[email] = ex['id']
        else:
            cur.execute(
                "INSERT INTO users (name,email,password_hash,role,bio,created_at) VALUES (?,?,?,?,?,?)",
                (name, email, hash_password(pwd), role, bio, ts(30))
            )
            uid_map[email] = cur.lastrowid

    # Get existing user IDs
    admin_id   = con.execute("SELECT id FROM users WHERE role='admin'").fetchone()['id']
    demo_id    = con.execute("SELECT id FROM users WHERE email='demo@student.com'").fetchone()['id']
    arjun_id   = uid_map.get('arjun@student.com', demo_id)
    priya_id   = uid_map.get('priya@student.com', demo_id)
    rohan_id   = uid_map.get('rohan@student.com', demo_id)
    sneha_id   = uid_map.get('sneha@student.com', demo_id)

    # ── Notes ────────────────────────────────────────────────
    notes = [
        {
            'user_id': arjun_id,
            'title': 'Data Structures & Algorithms — Complete Guide',
            'subject': 'Computer Science',
            'description': 'Comprehensive notes covering Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Sorting & Searching algorithms with time complexity analysis and Python code examples.',
            'tags': 'DSA,Python,Algorithms,Trees,Graphs',
            'file_type': 'pdf', 'file_size': 3354624,
            'views': 342, 'likes': 56, 'downloads': 89, 'days_ago': 60,
        },
        {
            'user_id': priya_id,
            'title': 'Machine Learning Fundamentals',
            'subject': 'Artificial Intelligence',
            'description': 'Core ML concepts: regression, classification, clustering, neural networks, model evaluation, bias-variance tradeoff, and hands-on Scikit-learn examples.',
            'tags': 'ML,Neural Networks,Scikit-learn,Regression',
            'file_type': 'pdf', 'file_size': 5347328,
            'views': 280, 'likes': 44, 'downloads': 67, 'days_ago': 50,
        },
        {
            'user_id': rohan_id,
            'title': 'Database Management Systems',
            'subject': 'Computer Science',
            'description': 'SQL queries, normalization (1NF–BCNF), ER diagrams, transaction management, ACID properties, indexing strategies, and NoSQL overview.',
            'tags': 'DBMS,SQL,Normalization,Transactions',
            'file_type': 'doc', 'file_size': 1887436,
            'views': 198, 'likes': 31, 'downloads': 52, 'days_ago': 40,
        },
        {
            'user_id': sneha_id,
            'title': 'Engineering Mathematics — Calculus & Linear Algebra',
            'subject': 'Mathematics',
            'description': 'Limits, derivatives, integrals, partial differentiation, matrices, eigenvalues, vector spaces, and Fourier series with fully worked examples.',
            'tags': 'Maths,Calculus,Linear Algebra,Fourier',
            'file_type': 'pdf', 'file_size': 4194304,
            'views': 175, 'likes': 28, 'downloads': 44, 'days_ago': 35,
        },
        {
            'user_id': arjun_id,
            'title': 'Operating Systems — Processes & Memory Management',
            'subject': 'Computer Science',
            'description': 'Process scheduling algorithms (FCFS, SJF, Round Robin), deadlock detection & avoidance, paging, segmentation, virtual memory, and file systems.',
            'tags': 'OS,Scheduling,Memory,Deadlock',
            'file_type': 'txt', 'file_size': 943718,
            'views': 155, 'likes': 22, 'downloads': 38, 'days_ago': 28,
        },
        {
            'user_id': priya_id,
            'title': 'Computer Networks — Protocols & Architecture',
            'subject': 'Networking',
            'description': 'OSI model layers, TCP/IP stack, HTTP/HTTPS, DNS resolution, routing protocols (OSPF, BGP), subnetting, CIDR, and network security fundamentals.',
            'tags': 'Networks,TCP-IP,OSI,Routing,Security',
            'file_type': 'pdf', 'file_size': 2830336,
            'views': 130, 'likes': 19, 'downloads': 31, 'days_ago': 20,
        },
        {
            'user_id': rohan_id,
            'title': 'Deep Learning with TensorFlow & Keras',
            'subject': 'Artificial Intelligence',
            'description': 'CNNs, RNNs, LSTMs, attention mechanisms, transfer learning, and practical implementation in TensorFlow 2.x with real-world project examples.',
            'tags': 'Deep Learning,TensorFlow,CNN,RNN,Keras',
            'file_type': 'pdf', 'file_size': 6291456,
            'views': 210, 'likes': 37, 'downloads': 55, 'days_ago': 15,
        },
        {
            'user_id': demo_id,
            'title': 'Python Programming — Beginner to Advanced',
            'subject': 'Computer Science',
            'description': 'Variables, data types, control flow, functions, OOP, file I/O, error handling, decorators, generators, and popular libraries (NumPy, Pandas, Matplotlib).',
            'tags': 'Python,OOP,Pandas,NumPy',
            'file_type': 'pdf', 'file_size': 3670016,
            'views': 95, 'likes': 14, 'downloads': 28, 'days_ago': 10,
        },
    ]

    note_ids = []
    for n in notes:
        ex = con.execute("SELECT id FROM notes WHERE title=?", (n['title'],)).fetchone()
        if ex:
            note_ids.append(ex['id'])
            continue
        # Generate filename from title
        filename = n['title'].lower().replace(' ', '_').replace('&', 'and')[:50] + f".{n['file_type']}"
        cur.execute(
            "INSERT INTO notes (user_id,title,subject,description,tags,filename,file_type,file_size,"
            "views,likes,downloads,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (n['user_id'], n['title'], n['subject'], n['description'], n['tags'],
             filename, n['file_type'], n['file_size'], n['views'], n['likes'], n['downloads'],
             ts(n['days_ago']))
        )
        note_ids.append(cur.lastrowid)

    # ── Comments ─────────────────────────────────────────────
    comment_templates = [
        (arjun_id,  "This is incredibly detailed! The time complexity section helped me ace my placement interview. Highly recommend!"),
        (priya_id,  "Great work on this. Could you add more examples on graph traversal algorithms?"),
        (rohan_id,  "Saved me hours before the exam. The diagrams are super clear. Thank you!"),
        (sneha_id,  "I was struggling with this topic — these notes made everything click. ⭐⭐⭐⭐⭐"),
        (demo_id,   "Very well organized. Would love to see a follow-up on advanced topics!"),
        (arjun_id,  "The practical examples are what make this stand out from textbooks."),
        (priya_id,  "Shared this with my entire study group. Everyone found it super useful!"),
    ]

    all_users = [admin_id, demo_id, arjun_id, priya_id, rohan_id, sneha_id]

    for idx, nid in enumerate(note_ids):
        # Add 2–4 comments per note
        for i, (uid, text) in enumerate(comment_templates[(idx % 3):(idx % 3) + 3]):
            if uid is None:
                continue
            cur.execute(
                "INSERT INTO comments (note_id,user_id,text,created_at) VALUES (?,?,?,?)",
                (nid, uid, text, ts(0, hours_ago=(i + 1) * 6))
            )

    # ── Ratings ──────────────────────────────────────────────
    rating_sets = [
        [5, 4, 5, 5, 4],   # note 0
        [5, 4, 5, 3, 5],   # note 1
        [4, 4, 3, 5, 4],   # note 2
        [4, 5, 4, 4, 3],   # note 3
        [4, 4, 5, 4, 5],   # note 4
        [3, 4, 4, 5, 4],   # note 5
        [5, 5, 4, 5, 5],   # note 6
        [4, 3, 4, 4, 5],   # note 7
    ]
    for idx, nid in enumerate(note_ids):
        stars_list = rating_sets[idx % len(rating_sets)]
        for uid, stars in zip(all_users, stars_list):
            con.execute(
                "INSERT OR IGNORE INTO ratings (note_id,user_id,stars,created_at) VALUES (?,?,?,?)",
                (nid, uid, stars, ts(idx + 1))
            )

    # ── Likes ────────────────────────────────────────────────
    for idx, nid in enumerate(note_ids):
        for uid in all_users[: (idx % 4) + 2]:
            con.execute(
                "INSERT OR IGNORE INTO likes (note_id,user_id,created_at) VALUES (?,?,?)",
                (nid, uid, ts(idx))
            )

    # ── Bookmarks ────────────────────────────────────────────
    bookmark_pairs = [
        (arjun_id, note_ids[1]), (arjun_id, note_ids[5]),
        (priya_id, note_ids[0]), (priya_id, note_ids[3]),
        (rohan_id, note_ids[0]), (rohan_id, note_ids[4]),
        (demo_id,  note_ids[2]), (demo_id,  note_ids[6]),
    ]
    for uid, nid in bookmark_pairs:
        if nid:
            con.execute(
                "INSERT OR IGNORE INTO bookmarks (note_id,user_id,created_at) VALUES (?,?,?)",
                (nid, uid, ts(5))
            )

    # ── Notifications ────────────────────────────────────────
    notifs = [
        (arjun_id, 'like',    '❤️',  f'Priya Sharma liked your note "Data Structures & Algorithms".', f'/note/{note_ids[0]}', ts(2)),
        (arjun_id, 'comment', '💬',  f'Rohan Das commented on your OS notes.',                         f'/note/{note_ids[4]}', ts(1)),
        (priya_id, 'like',    '❤️',  f'Sneha Iyer liked your ML Fundamentals notes.',                  f'/note/{note_ids[1]}', ts(3)),
        (rohan_id, 'comment', '💬',  f'Arjun Mehta commented on your DBMS notes.',                     f'/note/{note_ids[2]}', ts(4)),
        (demo_id,  'upload',  '📤',  f'Your note "Python Programming" was uploaded successfully.',      f'/note/{note_ids[7]}', ts(10)),
    ]
    for uid, typ, icon, msg, link, created in notifs:
        con.execute(
            "INSERT INTO notifications (user_id,type,message,link,read,created_at) VALUES (?,?,?,?,?,?)",
            (uid, typ, msg, link, 0, created)
        )

    con.commit()
    con.close()

    print("\n" + "=" * 54)
    print("  ✅  Seed data inserted successfully!")
    print("=" * 54)
    print(f"  👥  Users    : 6 (admin + 5 students)")
    print(f"  📄  Notes    : {len(note_ids)}")
    print(f"  💬  Comments : {len(note_ids) * 3} (approx)")
    print(f"  ⭐  Ratings  : {len(note_ids) * 6} (approx)")
    print(f"  ❤️  Likes    : seeded per note")
    print(f"  🔖  Bookmarks: {len(bookmark_pairs)}")
    print("=" * 54 + "\n")


if __name__ == '__main__':
    if not os.path.exists(DB):
        print("❌  Database not found. Run 'python app.py' first to initialise the DB.")
    else:
        run()
