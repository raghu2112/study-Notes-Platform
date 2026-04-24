# 📚 StudyNotes — Collaborative Study Platform

> A production-grade, full-featured collaborative study notes platform built with vanilla HTML, CSS, and JavaScript. No frameworks required — just open and run.

---

## 🌟 Live Demo Credentials

| Role    | Email                   | Password    |
|---------|-------------------------|-------------|
| Admin   | admin@studynotes.com    | Admin@123   |
| Student | arjun@student.com       | Student@1   |
| Student | priya@student.com       | Student@2   |
| Student | rohan@student.com       | Student@3   |

---

## 🚀 How to Run the Project

### Method 1 — Just Open It (Simplest)
```bash
# Navigate to the project folder and open index.html in any browser
open index.html        # macOS
start index.html       # Windows
xdg-open index.html    # Linux
```

### Method 2 — Local Development Server (Recommended)

**Using Python (no install needed):**
```bash
cd study-notes-platform
python3 -m http.server 8000
# Open http://localhost:8000 in your browser
```

**Using Node.js (npx serve):**
```bash
npx serve study-notes-platform
# Opens automatically in browser
```

**Using VS Code Live Server:**
1. Install the "Live Server" extension in VS Code
2. Right-click `index.html` → "Open with Live Server"

---

## 📁 Project Structure

```
study-notes-platform/
│
├── index.html              # Main SPA HTML — all views defined here
│
├── css/
│   └── styles.css          # Complete design system (1000+ lines)
│                           # Tokens, components, responsive, animations
│
├── js/
│   ├── data.js             # Data layer — localStorage CRUD, schema, seed
│   └── app.js              # App logic — Auth, Notes, Views, Admin, UI utils
│
└── README.md               # This file
```

---

## 🏗️ Architecture Overview

The app is a **Single Page Application (SPA)** with a custom routing system:

```
┌─────────────────────────────────────────────────────────┐
│                        index.html                       │
│  ┌──────────────┐   ┌────────────────────────────────┐  │
│  │  Auth Screen │   │         App Layout             │  │
│  │  Login       │   │  Sidebar + Header + Views      │  │
│  │  Register    │   │                                │  │
│  └──────────────┘   │  Views:                        │  │
│                     │  • Dashboard                   │  │
│  js/data.js         │  • Browse Notes                │  │
│  ┌──────────────┐   │  • Note Detail                 │  │
│  │  DB Object   │   │  • Bookmarks                   │  │
│  │  Users       │   │  • Profile                     │  │
│  │  Notes       │   │  • Notifications               │  │
│  │  Comments    │   │  • Admin Panel                 │  │
│  │  Notifs      │   └────────────────────────────────┘  │
│  └──────────────┘                                       │
│  js/app.js          Data stored in localStorage        │
│  ┌──────────────────────────────────────────┐          │
│  │  App | Auth | Notes | Views | Admin | UI │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Data Schema

### User
```json
{
  "id": "u_abc123",
  "name": "Arjun Mehta",
  "email": "arjun@student.com",
  "password": "Student@1",
  "role": "student | admin",
  "bio": "B.Tech CSE 3rd year",
  "joinDate": "ISO_DATE",
  "bookmarks": ["note_id_1", "note_id_2"],
  "likedNotes": ["note_id_1"],
  "likedComments": ["comment_id_1"],
  "avatar": "AM",
  "notifCount": 2
}
```

### Note
```json
{
  "id": "n_abc123",
  "title": "Data Structures Complete Guide",
  "subject": "Computer Science",
  "description": "Comprehensive coverage of DSA...",
  "tags": ["DSA", "Python", "Algorithms"],
  "fileType": "pdf | doc | txt",
  "fileSize": "3.2 MB",
  "author": "Arjun Mehta",
  "authorId": "u_abc123",
  "uploadDate": "ISO_DATE",
  "views": 342,
  "downloads": 89,
  "likes": 56,
  "rating": 4.7,
  "ratingCount": 38,
  "banner": "#1a3a6e"
}
```

### Comment
```json
{
  "id": "c_abc123",
  "noteId": "n_abc123",
  "userId": "u_abc123",
  "userName": "Priya Sharma",
  "avatar": "PS",
  "text": "This note is very helpful!",
  "date": "ISO_DATE",
  "likes": 5
}
```

### Notification
```json
{
  "id": "notif_123",
  "userId": "u_abc123",
  "type": "like | comment | upload",
  "icon": "👍",
  "bg": "rgba(79,141,255,0.15)",
  "message": "<strong>Priya</strong> liked your note.",
  "date": "ISO_DATE",
  "read": false
}
```

---

## 🎨 UI/UX Design Decisions

### Aesthetic Direction: "Deep-Space Academic"
A sophisticated dark-mode-first design that feels like a premium ed-tech product.

| Choice | Rationale |
|--------|-----------|
| **Font: Syne** (headings) | Geometric, bold — commands attention without shouting |
| **Font: Nunito** (body) | Friendly, highly legible — perfect for long reading sessions |
| **Color: #4F8DFF accent** | Electric blue — energetic yet professional; avoids purple cliché |
| **Color: #06D6A0** secondary | Teal-green contrast — signals success, freshness, growth |
| **Color: #FFD166** warning | Warm amber — star ratings, warmth, approachable feel |
| **Dark background (#070C1B)** | Reduces eye strain for long study sessions |
| **Card hover elevation** | Subtle translateY(-4px) signals interactivity without jarring the eye |
| **Glass-morphism borders** | Modern depth without heavy shadows on dark backgrounds |
| **Grain texture overlay** | Adds texture, prevents UI from feeling too "flat/digital" |
| **Animated stat counters** | Provides satisfaction and visual feedback on page load |
| **Staggered card animations** | animation-delay per card creates a natural reveal sequence |

### Responsive Strategy
- Desktop: 260px fixed sidebar + fluid main content
- Tablet: Sidebar collapses, accessible via hamburger button
- Mobile: Full-width cards, bottom-friendly touch targets

---

## ✅ Feature Checklist

| Feature | Status |
|---------|--------|
| Login / Register with validation | ✅ |
| Role-based access (Student + Admin) | ✅ |
| Note upload (file type + size validation) | ✅ |
| Upload progress bar animation | ✅ |
| Notes grid with card layout | ✅ |
| Search (by title, subject, tag, author) | ✅ |
| Filter by subject + sort options | ✅ |
| Pagination (with smart ellipsis) | ✅ |
| Note detail view with stats | ✅ |
| Star rating system | ✅ |
| Like / Unlike notes | ✅ |
| Bookmark / Unbookmark notes | ✅ |
| Download notes (with counter) | ✅ |
| View counter per note | ✅ |
| Comment section | ✅ |
| Like comments | ✅ |
| Delete comments (own + admin) | ✅ |
| Notifications panel + full view | ✅ |
| Profile page with stats | ✅ |
| Edit profile (name, bio) | ✅ |
| Admin: User management table | ✅ |
| Admin: Notes management table | ✅ |
| Admin: Delete users and notes | ✅ |
| Dark/Light mode toggle | ✅ |
| Trending notes section | ✅ |
| Activity feed on dashboard | ✅ |
| Weekly activity bar chart | ✅ |
| Toast notification system | ✅ |
| Confirmation dialog | ✅ |
| Keyboard shortcut (Esc closes modal) | ✅ |
| Responsive mobile layout | ✅ |
| LocalStorage persistence | ✅ |
| Seed demo data on first run | ✅ |
| Grid / List view toggle | ✅ |

---

## ️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Markup | HTML5 (Semantic) |
| Styles | CSS3 (Custom Properties, Grid, Flexbox, Animations) |
| Logic | Vanilla JavaScript (ES6+ modules pattern) |
| Fonts | Google Fonts (Syne + Nunito) |
| Storage | localStorage (browser-native) |
| Icons | Unicode Emoji (zero-dependency) |

**Total bundle size: ~80 KB** (HTML + CSS + JS, uncompressed, no frameworks)

---

## 🎛️ UI Technologies & Advanced Features

### CSS3 Technologies Implemented
| Technology | Usage | Examples |
|-----------|-------|----------|
| **CSS Grid** | Complex multi-column layouts | Notes grid, admin tables, dashboard stats |
| **Flexbox** | Flexible component layouts | Navigation sidebar, headers, card layouts |
| **CSS Custom Properties (Variables)** | 50+ dynamic theme tokens | Color system, spacing, shadows, transitions |
| **CSS Animations** | Smooth keyframe-based motion | Fade-in, slide-in, pulse, float, staggered reveals |
| **CSS Transforms** | 2D/3D motion & effects | translateY, scale, rotate for interactive feedback |
| **CSS Gradients** | Multi-color visual effects | Linear & radial gradients for backgrounds & accents |
| **Media Queries** | Responsive breakpoints | Mobile (320px+), Tablet (768px+), Desktop (1024px+) |
| **Backdrop Filters** | Glass-morphism effects | Modern frosted-glass card borders |
| **SVG Filters** | Procedural texture overlays | Noise/grain texture for depth on dark backgrounds |
| **Box-Shadow & Glow Effects** | Elevation & depth | Multiple shadow layers, accent glows, hover elevation |
| **CSS Transitions** | Smooth property animations | Cubic-bezier timing for natural easing (0.22s average) |

### JavaScript Features & Patterns
| Feature | Purpose | Implementation |
|---------|---------|-----------------|
| **Event Delegation** | Efficient event handling | Click handlers on containers, event.target detection |
| **localStorage API** | Persistent client-side storage | User sessions, note data, UI preferences |
| **DOM Manipulation** | Dynamic content rendering | innerHTML, classList, appendChild for SPA routing |
| **ES6+ Features** | Modern JavaScript syntax | Arrow functions, destructuring, template literals, const/let |
| **Debouncing** | Performance optimization | Search input, form validation, resize handlers |
| **Async Operations** | Non-blocking tasks | File uploads, data persistence, animations |
| **Regex Validation** | Form input validation | Email, password strength, file extensions |
| **Array Methods** | Data processing | filter(), map(), sort(), reduce() for note/user operations |
| **Object Prototypes** | Code organization | DB, Auth, Notes, Admin modules with shared methods |

### HTML5 Semantic Structure
| Element | Usage |
|---------|-------|
| `<nav>` | Sidebar navigation with keyboard shortcuts |
| `<article>` | Note cards and note detail views |
| `<section>` | Logical content grouping (dashboard, trending, admin) |
| `<header>` | Page headers with breadcrumbs and search |
| `<footer>` | Sidebar footer with user profile quick-link |
| `<form>` | Login, register, upload, edit profile forms |
| `<input type="*">` | Text, email, password, file, date, range inputs |
| `<dialog>` / Modal patterns | Modal dialogs for confirmations & modals |

### Interactive UI Components Built
| Component | Features |
|-----------|----------|
| **Modal Dialogs** | Overlay, focus trap, Esc key to close, smooth animations |
| **Toast Notifications** | Stacked auto-dismiss toasts, success/error/info styling |
| **Progress Bar** | File upload progress visualization with percentage |
| **Star Rating System** | 5-star interactive rating, hover preview, click to submit |
| **Pagination Controls** | Previous/Next buttons, numbered pages, smart ellipsis (...) |
| **Search & Filter UI** | Real-time search, subject filters, sort dropdown |
| **Drag-and-Drop Zone** | Visual feedback, hover state, file preview |
| **Confirmation Dialogs** | Two-button confirm/cancel with destructive action warnings |
| **Toggle Switches** | Dark/Light mode toggle, Grid/List view switch |
| **Countdown Timers** | Animated stat counters on dashboard load |
| **Animated Charts** | Weekly activity bar chart with smooth animations |
| **Tab Navigation** | Admin panel tabs for Users/Notes management |

### Animation & Motion Design
| Animation Type | Timing | Use Case |
|---|---|---|
| **Fade & Slide In** | 0.35s ease | View transitions (fadeSlideIn keyframes) |
| **Hover Elevation** | 0.22s cubic-bezier | Card hover, button press feedback |
| **Pulse Glow** | 6-8s infinite | Background accent orbs on auth screens |
| **Float Motion** | 4s ease-in-out infinite | Hero orb floating animation |
| **Staggered Reveals** | animation-delay per card | Notes grid cards reveal in sequence |
| **Spinner Rotation** | Linear infinite | Loading states for async operations |
| **Progress Fill** | Linear | Upload progress bar fill animation |

### Responsive Design Breakpoints
```css
/* Mobile First Approach */
Base:     320px (all devices)
Tablet:   768px (iPad, Android tablets)
Desktop: 1024px (laptops, desktops)
Wide:    1440px (ultrawide monitors)

Sidebar Behavior:
• Desktop: 260px fixed sidebar always visible
• Tablet:  Sidebar hidden by default, toggle via hamburger
• Mobile:  Full-width layout, sidebar as overlay drawer
```

### Accessibility Features
| Feature | Implementation |
|---------|-----------------|
| **Keyboard Navigation** | Tab through form fields, Esc to close modals |
| **Focus Indicators** | Visible focus rings on interactive elements |
| **Semantic HTML** | Proper heading hierarchy (H1→H6), nav landmarks |
| **Color Contrast** | WCAG AA compliant text/background ratios |
| **Form Labels** | Proper <label> elements linked to inputs |
| **ARIA Attributes** | role, aria-label, aria-expanded for screen readers |
| **Button States** | Disabled states for invalid forms |
| **Status Messages** | Toast notifications for user feedback |

### Design System & Theme Variables
**50+ CSS Custom Properties organized by category:**
- **Colors** (8 base, 10 functional) — Primary, secondary, accent, danger, warning, success
- **Spacing** (12 scale) — 4px → 64px incremental spacing scale
- **Typography** (6 font-sizes) — 0.68rem (small) → 2.2rem (hero)
- **Shadows** (4 levels) — Soft to strong elevation shadows
- **Radii** (4 border-radius) — sm (8px) → full (999px)
- **Transitions** (2 timing functions) — 0.22s snappy, 0.4s slow
- **Layers** (CSS variables for z-index) — Modal > Dropdown > Card > Base

### Performance Optimizations
| Technique | Benefit |
|-----------|---------|
| **Hardware Acceleration** | transform/opacity for 60fps animations |
| **Lazy CSS Selectors** | Efficient DOM queries, class-based selection |
| **Minimal Reflows** | Batch DOM updates, avoid forced layouts |
| **Debounced Events** | Reduce listener firing for scroll/resize/input |
| **Local Asset Loading** | No external CDN dependencies except Google Fonts |
| **Zero JS Frameworks** | Direct DOM API for lightweight execution |

---

## 📝 Evaluation Notes

This project demonstrates:

1. **Clean Architecture** — Data layer (data.js) is fully separated from UI logic (app.js)
2. **Real-world UX patterns** — Modals, toasts, confirmations, loading states, empty states
3. **Form UX** — Validation with inline errors, password toggle, drag-and-drop upload
4. **Role-based access** — Admin-only UI elements conditionally rendered
5. **State management** — localStorage as persistent state, current user in session
6. **Responsive design** — Works on mobile, tablet, and desktop
7. **Accessibility** — Keyboard navigation (Esc key), semantic HTML, focus management
8. **Performance** — Debounced search, staggered animations, minimal DOM manipulation
9. **Design system** — 50+ CSS custom properties for consistent theming

---

*Built with ❤️ for the Collaborative Study Notes Platform assignment*
