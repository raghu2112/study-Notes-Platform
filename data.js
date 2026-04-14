/**
 * DATA LAYER — StudyNotes Platform
 * Manages all data persistence via localStorage.
 * Schema: Users, Notes, Comments, Notifications
 */

const DB = {

  /* ──────────────────────────────────────
     KEYS
  ────────────────────────────────────── */
  KEYS: {
    USERS:         'snp_users',
    NOTES:         'snp_notes',
    COMMENTS:      'snp_comments',
    NOTIFICATIONS: 'snp_notifications',
    CURRENT_USER:  'snp_current_user',
    SETTINGS:      'snp_settings',
  },

  /* ──────────────────────────────────────
     GENERIC HELPERS
  ────────────────────────────────────── */
  get(key)         { try { return JSON.parse(localStorage.getItem(key)) || []; } catch { return []; } },
  getObj(key)      { try { return JSON.parse(localStorage.getItem(key)) || {}; } catch { return {}; } },
  set(key, value)  { localStorage.setItem(key, JSON.stringify(value)); },
  uid()            { return '_' + Math.random().toString(36).slice(2,11) + Date.now().toString(36); },
  now()            { return new Date().toISOString(); },
  timeAgo(iso) {
    const diff = Date.now() - new Date(iso).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1)  return 'just now';
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    const d = Math.floor(h / 24);
    if (d < 30) return `${d}d ago`;
    return new Date(iso).toLocaleDateString();
  },

  /* ──────────────────────────────────────
     SEED DATA  (runs once on first load)
  ────────────────────────────────────── */
  seed() {
    if (localStorage.getItem('snp_seeded')) return;

    /* ── Admin + students ── */
    const users = [
      {
        id: 'u_admin01',
        name: 'Dr. Admin Singh',
        email: 'admin@studynotes.com',
        password: 'Admin@123',
        role: 'admin',
        bio: 'Platform administrator & Computer Science faculty.',
        joinDate: '2024-01-10T08:00:00.000Z',
        bookmarks: [],
        likedNotes: [],
        likedComments: [],
        avatar: 'DS',
        notifCount: 0,
      },
      {
        id: 'u_stu01',
        name: 'Arjun Mehta',
        email: 'arjun@student.com',
        password: 'Student@1',
        role: 'student',
        bio: 'B.Tech CSE 3rd year | Loves Data Structures & ML.',
        joinDate: '2024-02-15T10:00:00.000Z',
        bookmarks: ['n_003', 'n_005'],
        likedNotes: ['n_001', 'n_002'],
        likedComments: [],
        avatar: 'AM',
        notifCount: 2,
      },
      {
        id: 'u_stu02',
        name: 'Priya Sharma',
        email: 'priya@student.com',
        password: 'Student@2',
        role: 'student',
        bio: 'ECE enthusiast | Note-taker extraordinaire.',
        joinDate: '2024-03-01T09:00:00.000Z',
        bookmarks: ['n_001'],
        likedNotes: ['n_003'],
        likedComments: [],
        avatar: 'PS',
        notifCount: 1,
      },
      {
        id: 'u_stu03',
        name: 'Rohan Das',
        email: 'rohan@student.com',
        password: 'Student@3',
        role: 'student',
        bio: '2nd year AIML | Python & TensorFlow aficionado.',
        joinDate: '2024-03-20T11:00:00.000Z',
        bookmarks: [],
        likedNotes: ['n_004'],
        likedComments: [],
        avatar: 'RD',
        notifCount: 0,
      },
    ];

    /* ── Notes ── */
    const notes = [
      {
        id: 'n_001',
        title: 'Data Structures & Algorithms — Complete Guide',
        subject: 'Computer Science',
        description: 'Comprehensive notes covering Arrays, Linked Lists, Trees, Graphs, Sorting & Searching algorithms with time complexity analysis and Python examples.',
        tags: ['DSA', 'Python', 'Algorithms', 'Trees'],
        fileType: 'pdf',
        fileSize: '3.2 MB',
        author: 'Arjun Mehta',
        authorId: 'u_stu01',
        uploadDate: '2024-10-01T10:00:00.000Z',
        views: 342,
        downloads: 89,
        likes: 56,
        rating: 4.7,
        ratingCount: 38,
        banner: '#1a3a6e',
        fileData: null,
      },
      {
        id: 'n_002',
        title: 'Machine Learning Fundamentals',
        subject: 'Artificial Intelligence',
        description: 'Core ML concepts: regression, classification, clustering, neural networks, model evaluation, and hands-on Scikit-learn examples.',
        tags: ['ML', 'Neural Networks', 'Scikit-learn'],
        fileType: 'pdf',
        fileSize: '5.1 MB',
        author: 'Priya Sharma',
        authorId: 'u_stu02',
        uploadDate: '2024-10-08T14:00:00.000Z',
        views: 280,
        downloads: 67,
        likes: 44,
        rating: 4.5,
        ratingCount: 29,
        banner: '#1a4a35',
        fileData: null,
      },
      {
        id: 'n_003',
        title: 'Database Management Systems',
        subject: 'Computer Science',
        description: 'SQL queries, normalization forms (1NF–BCNF), ER diagrams, transaction management, indexing, and NoSQL overview.',
        tags: ['DBMS', 'SQL', 'Normalization'],
        fileType: 'doc',
        fileSize: '1.8 MB',
        author: 'Rohan Das',
        authorId: 'u_stu03',
        uploadDate: '2024-10-15T11:00:00.000Z',
        views: 198,
        downloads: 52,
        likes: 31,
        rating: 4.3,
        ratingCount: 21,
        banner: '#3a1a50',
        fileData: null,
      },
      {
        id: 'n_004',
        title: 'Engineering Mathematics — Calculus & Linear Algebra',
        subject: 'Mathematics',
        description: 'Limits, derivatives, integrals, matrices, eigenvalues, vector spaces, and Fourier series with solved examples.',
        tags: ['Maths', 'Calculus', 'Linear Algebra'],
        fileType: 'pdf',
        fileSize: '4.0 MB',
        author: 'Arjun Mehta',
        authorId: 'u_stu01',
        uploadDate: '2024-10-22T09:00:00.000Z',
        views: 175,
        downloads: 44,
        likes: 28,
        rating: 4.1,
        ratingCount: 18,
        banner: '#4a2a10',
        fileData: null,
      },
      {
        id: 'n_005',
        title: 'Operating Systems — Processes & Memory',
        subject: 'Computer Science',
        description: 'Process scheduling algorithms, deadlock detection & avoidance, memory management (paging, segmentation), virtual memory, and file systems.',
        tags: ['OS', 'Scheduling', 'Memory Management'],
        fileType: 'txt',
        fileSize: '0.9 MB',
        author: 'Priya Sharma',
        authorId: 'u_stu02',
        uploadDate: '2024-11-01T13:00:00.000Z',
        views: 155,
        downloads: 38,
        likes: 22,
        rating: 4.2,
        ratingCount: 14,
        banner: '#1a3050',
        fileData: null,
      },
      {
        id: 'n_006',
        title: 'Computer Networks — Protocols & Architecture',
        subject: 'Networking',
        description: 'OSI model, TCP/IP stack, HTTP/HTTPS, DNS, routing protocols (OSPF, BGP), subnetting, and network security basics.',
        tags: ['Networks', 'TCP/IP', 'OSI', 'Security'],
        fileType: 'pdf',
        fileSize: '2.7 MB',
        author: 'Rohan Das',
        authorId: 'u_stu03',
        uploadDate: '2024-11-10T15:00:00.000Z',
        views: 130,
        downloads: 31,
        likes: 19,
        rating: 4.0,
        ratingCount: 12,
        banner: '#2a1a40',
        fileData: null,
      },
    ];

    /* ── Comments ── */
    const comments = [
      { id: 'c_001', noteId: 'n_001', userId: 'u_stu02', userName: 'Priya Sharma', avatar: 'PS', text: 'This is incredibly detailed! The time complexity section helped me crack my placement interview. Highly recommend!', date: '2024-10-05T12:00:00.000Z', likes: 12 },
      { id: 'c_002', noteId: 'n_001', userId: 'u_stu03', userName: 'Rohan Das', avatar: 'RD', text: 'Great work Arjun. Could you also add notes on Graph algorithms like Dijkstra and BFS/DFS in more detail?', date: '2024-10-06T09:30:00.000Z', likes: 7 },
      { id: 'c_003', noteId: 'n_002', userId: 'u_stu01', userName: 'Arjun Mehta', avatar: 'AM', text: 'The Scikit-learn examples are hands-on and super practical. Perfect for our ML lab assignments!', date: '2024-10-12T16:00:00.000Z', likes: 9 },
      { id: 'c_004', noteId: 'n_003', userId: 'u_stu02', userName: 'Priya Sharma', avatar: 'PS', text: 'ER diagrams were explained beautifully. Cleared a lot of my doubts before the university exam.', date: '2024-10-18T11:00:00.000Z', likes: 5 },
      { id: 'c_005', noteId: 'n_004', userId: 'u_stu03', userName: 'Rohan Das', avatar: 'RD', text: 'I was struggling with eigenvalues and this really helped me visualise the concept. Thank you!', date: '2024-10-25T14:00:00.000Z', likes: 4 },
    ];

    /* ── Notifications ── */
    const notifications = [
      { id: 'notif_1', userId: 'u_stu01', type: 'like', icon: '👍', bg: 'rgba(79,141,255,0.15)', message: '<strong>Priya Sharma</strong> liked your note on DSA.', date: '2024-10-05T12:30:00.000Z', read: false },
      { id: 'notif_2', userId: 'u_stu01', type: 'comment', icon: '💬', bg: 'rgba(6,214,160,0.15)', message: '<strong>Rohan Das</strong> commented on your DSA notes.', date: '2024-10-06T09:30:00.000Z', read: false },
      { id: 'notif_3', userId: 'u_stu02', type: 'like', icon: '⭐', bg: 'rgba(255,209,102,0.15)', message: '<strong>Arjun Mehta</strong> rated your ML notes 5 stars!', date: '2024-10-12T16:10:00.000Z', read: false },
    ];

    this.set(this.KEYS.USERS, users);
    this.set(this.KEYS.NOTES, notes);
    this.set(this.KEYS.COMMENTS, comments);
    this.set(this.KEYS.NOTIFICATIONS, notifications);
    this.set(this.KEYS.SETTINGS, { theme: 'dark' });
    localStorage.setItem('snp_seeded', '1');
  },

  /* ──────────────────────────────────────
     USERS
  ────────────────────────────────────── */
  Users: {
    all()         { return DB.get(DB.KEYS.USERS); },
    byId(id)      { return this.all().find(u => u.id === id) || null; },
    byEmail(e)    { return this.all().find(u => u.email.toLowerCase() === e.toLowerCase()) || null; },
    save(users)   { DB.set(DB.KEYS.USERS, users); },

    create({ name, email, password, role }) {
      const users = this.all();
      if (this.byEmail(email)) return { ok: false, error: 'Email already registered.' };
      const user = {
        id: DB.uid(), name, email, password, role: role || 'student',
        bio: '', joinDate: DB.now(), bookmarks: [], likedNotes: [],
        likedComments: [], avatar: name.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2),
        notifCount: 0,
      };
      users.push(user);
      this.save(users);
      return { ok: true, user };
    },

    login(email, password) {
      const user = this.byEmail(email);
      if (!user) return { ok: false, error: 'No account found with this email.' };
      if (user.password !== password) return { ok: false, error: 'Incorrect password.' };
      DB.set(DB.KEYS.CURRENT_USER, user);
      return { ok: true, user };
    },

    logout() { localStorage.removeItem(DB.KEYS.CURRENT_USER); },

    current() { return DB.getObj(DB.KEYS.CURRENT_USER) || null; },

    update(id, fields) {
      const users = this.all();
      const idx = users.findIndex(u => u.id === id);
      if (idx === -1) return;
      users[idx] = { ...users[idx], ...fields };
      this.save(users);
      const cur = this.current();
      if (cur && cur.id === id) DB.set(DB.KEYS.CURRENT_USER, users[idx]);
      return users[idx];
    },

    toggleBookmark(userId, noteId) {
      const users = this.all();
      const u = users.find(u => u.id === userId);
      if (!u) return;
      const idx = u.bookmarks.indexOf(noteId);
      if (idx > -1) u.bookmarks.splice(idx, 1);
      else u.bookmarks.push(noteId);
      this.save(users);
      const cur = this.current();
      if (cur && cur.id === userId) DB.set(DB.KEYS.CURRENT_USER, u);
      return u.bookmarks.includes(noteId);
    },

    toggleLikeNote(userId, noteId) {
      const users = this.all();
      const u = users.find(u => u.id === userId);
      if (!u) return false;
      const idx = u.likedNotes.indexOf(noteId);
      if (idx > -1) u.likedNotes.splice(idx, 1);
      else u.likedNotes.push(noteId);
      this.save(users);
      if (this.current()?.id === userId) DB.set(DB.KEYS.CURRENT_USER, u);
      return u.likedNotes.includes(noteId);
    },

    delete(id) {
      this.save(this.all().filter(u => u.id !== id));
    },
  },

  /* ──────────────────────────────────────
     NOTES
  ────────────────────────────────────── */
  Notes: {
    all()       { return DB.get(DB.KEYS.NOTES); },
    byId(id)    { return this.all().find(n => n.id === id) || null; },
    save(notes) { DB.set(DB.KEYS.NOTES, notes); },

    byAuthor(authorId) { return this.all().filter(n => n.authorId === authorId); },

    create(data) {
      const notes = this.all();
      const note = {
        id: DB.uid(), ...data,
        uploadDate: DB.now(), views: 0, downloads: 0,
        likes: 0, rating: 0, ratingCount: 0,
        banner: ['#1a3a6e','#1a4a35','#3a1a50','#4a2a10','#1a3050','#2a1a40'][Math.floor(Math.random()*6)],
        fileData: data.fileData || null,
      };
      notes.unshift(note);
      this.save(notes);
      return note;
    },

    delete(id) { this.save(this.all().filter(n => n.id !== id)); },

    update(id, fields) {
      const notes = this.all();
      const idx = notes.findIndex(n => n.id === id);
      if (idx === -1) return;
      notes[idx] = { ...notes[idx], ...fields };
      this.save(notes);
      return notes[idx];
    },

    incrementViews(id) {
      const notes = this.all();
      const n = notes.find(n => n.id === id);
      if (n) { n.views++; this.save(notes); }
    },

    incrementDownloads(id) {
      const notes = this.all();
      const n = notes.find(n => n.id === id);
      if (n) { n.downloads++; this.save(notes); }
    },

    toggleLike(id, liked) {
      const notes = this.all();
      const n = notes.find(n => n.id === id);
      if (!n) return;
      n.likes += liked ? 1 : -1;
      if (n.likes < 0) n.likes = 0;
      this.save(notes);
      return n.likes;
    },

    addRating(id, stars) {
      const notes = this.all();
      const n = notes.find(n => n.id === id);
      if (!n) return;
      const total = n.rating * n.ratingCount + stars;
      n.ratingCount++;
      n.rating = parseFloat((total / n.ratingCount).toFixed(1));
      this.save(notes);
      return n.rating;
    },

    search(query, subject, sort) {
      let notes = this.all();
      if (query) {
        const q = query.toLowerCase();
        notes = notes.filter(n =>
          n.title.toLowerCase().includes(q) ||
          n.description.toLowerCase().includes(q) ||
          n.tags.some(t => t.toLowerCase().includes(q)) ||
          n.author.toLowerCase().includes(q)
        );
      }
      if (subject && subject !== 'all') {
        notes = notes.filter(n => n.subject === subject);
      }
      switch (sort) {
        case 'popular': notes.sort((a,b) => b.likes - a.likes); break;
        case 'rating':  notes.sort((a,b) => b.rating - a.rating); break;
        case 'views':   notes.sort((a,b) => b.views - a.views); break;
        default:        notes.sort((a,b) => new Date(b.uploadDate) - new Date(a.uploadDate));
      }
      return notes;
    },

    trending(limit=5) {
      return this.all().sort((a,b) => b.views + b.likes*2 - (a.views + a.likes*2)).slice(0, limit);
    },

    recent(limit=6) {
      return this.all().sort((a,b) => new Date(b.uploadDate) - new Date(a.uploadDate)).slice(0, limit);
    },

    subjects() {
      return [...new Set(this.all().map(n => n.subject))];
    },
  },

  /* ──────────────────────────────────────
     COMMENTS
  ────────────────────────────────────── */
  Comments: {
    all()               { return DB.get(DB.KEYS.COMMENTS); },
    forNote(noteId)     { return this.all().filter(c => c.noteId === noteId).sort((a,b) => new Date(b.date) - new Date(a.date)); },
    save(c)             { DB.set(DB.KEYS.COMMENTS, c); },

    add({ noteId, userId, userName, avatar, text }) {
      const comments = this.all();
      const c = { id: DB.uid(), noteId, userId, userName, avatar, text, date: DB.now(), likes: 0 };
      comments.push(c);
      this.save(comments);
      return c;
    },

    delete(id) { this.save(this.all().filter(c => c.id !== id)); },

    toggleLike(id, userId) {
      const users = DB.Users.all();
      const u = users.find(u => u.id === userId);
      const comments = this.all();
      const c = comments.find(c => c.id === id);
      if (!u || !c) return;
      const idx = u.likedComments.indexOf(id);
      if (idx > -1) { u.likedComments.splice(idx,1); c.likes = Math.max(0, c.likes - 1); }
      else           { u.likedComments.push(id); c.likes++; }
      DB.Users.save(users);
      if (DB.Users.current()?.id === userId) DB.set(DB.KEYS.CURRENT_USER, u);
      this.save(comments);
      return { liked: u.likedComments.includes(id), count: c.likes };
    },
  },

  /* ──────────────────────────────────────
     NOTIFICATIONS
  ────────────────────────────────────── */
  Notifications: {
    all()           { return DB.get(DB.KEYS.NOTIFICATIONS); },
    forUser(userId) { return this.all().filter(n => n.userId === userId).sort((a,b) => new Date(b.date) - new Date(a.date)); },
    save(n)         { DB.set(DB.KEYS.NOTIFICATIONS, n); },
    unreadCount(userId) { return this.forUser(userId).filter(n => !n.read).length; },

    add({ userId, type, icon, bg, message }) {
      const notifs = this.all();
      notifs.push({ id: DB.uid(), userId, type, icon, bg, message, date: DB.now(), read: false });
      this.save(notifs);
    },

    markAllRead(userId) {
      const notifs = this.all().map(n => n.userId === userId ? { ...n, read: true } : n);
      this.save(notifs);
    },
  },

  /* ──────────────────────────────────────
     SETTINGS
  ────────────────────────────────────── */
  Settings: {
    get()           { return DB.getObj(DB.KEYS.SETTINGS); },
    set(key, val)   { const s = this.get(); s[key] = val; DB.set(DB.KEYS.SETTINGS, s); },
    theme()         { return this.get().theme || 'dark'; },
  },
};
