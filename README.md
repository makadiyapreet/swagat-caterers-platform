<div align="center">

# 🍽️ Swagat Caterers — Enterprise Catering Management Platform

**A production-grade, full-stack catering management system powering real business operations.**

![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.16-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/Deployed-AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

[🌐 Live Website](https://swagatcaterers.in) · [📧 Contact](#-contact--author) · [🚀 Features](#-features)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Code Protection Notice](#%EF%B8%8F-code-protection-notice)
- [Features](#-features)
- [Role-Based Access Control](#-role-based-access-control)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [System Architecture](#%EF%B8%8F-system-architecture)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Pages & Templates](#-pages--templates)
- [Authentication & Security](#-authentication--security)
- [Email & Notification System](#-email--notification-system)
- [Environment Variables](#-environment-variables)
- [Local Development Setup](#-local-development-setup)
- [Deployment](#-deployment)
- [Contact & Author](#-contact--author)
- [License](#-license)

---

## 🎯 Overview

**Swagat Caterers** is a comprehensive, enterprise-grade catering management platform built with **Django 6.0** and **Django REST Framework 3.16**. It digitizes every aspect of a catering business — from public-facing menu browsing and online booking to internal event management, staff tracking, task assignment, financial analytics, and automated billing.

The platform is not a portfolio demo. It is a **live, production system** actively powering catering operations at [swagatcaterers.in](https://swagatcaterers.in), serving real customers and managing real events.

### What Makes It Special

| Aspect | Details |
|--------|---------|
| **Real Business** | Actively serving a catering operation in Rajkot, Gujarat |
| **4-Tier Roles** | Admin → Manager → Staff → Customer, each with precise permissions |
| **Bilingual** | Complete English & Gujarati support across menus and UI |
| **Cloud-Native** | AWS EC2 hosting, Cloudinary CDN, Brevo transactional email |
| **20+ Models** | Comprehensive schema covering users, events, menus, bookings, tasks, notes, analytics |
| **30+ Pages** | Full-featured web application with SSR templates and REST APIs |

---

## ⚠️ Code Protection Notice

> **🔒 This is a CLOSED-SOURCE, PROPRIETARY project.**

This repository is **public for viewing and evaluation purposes only**.

**❌ Not Permitted:** Copying, cloning, forking, modifying, redistributing, or using any part of this code in your own projects — commercial or personal — without explicit written permission.

**✅ Permitted:** Viewing the code for learning, evaluating the project for employment or collaboration, and providing feedback to the author.

All code, designs, and intellectual property are owned exclusively by **Preet Makadiya** and **Swagat Caterers**. Unauthorized use will be pursued legally.

**For licensing or collaboration:** [swagatcaterersofficial@gmail.com](mailto:swagatcaterersofficial@gmail.com)

---

## ✨ Features

### 🌐 Public-Facing (No Login Required)

| Feature | Description |
|---------|-------------|
| **Home Page** | Hero section, featured packages, testimonials, stats counter, FAQ, and call-to-action banners |
| **Interactive Menu** | Categorized menu browsing with images and bilingual support (English / Gujarati) |
| **Custom Menu Builder** | Drag-and-drop menu customization with live per-plate price estimation |
| **Online Booking** | Multi-step booking form with automated email confirmation to the business |
| **Availability Calendar** | Real-time event calendar with FullCalendar.js integration |
| **Gallery** | Event photography showcase with admin-managed uploads |
| **Contact** | Multi-channel contact (form, WhatsApp, email, phone) with embedded Google Maps |
| **Menu PDFs** | Downloadable English and Gujarati menu cards |
| **AI Chatbot** | Conversational assistant for menu queries and booking guidance |
| **PWA** | Installable Progressive Web App with offline-capable manifest |

### 🔒 Admin Dashboard

| Feature | Description |
|---------|-------------|
| **Event Management** | Full CRUD for catering events with status tracking (Pending / Confirmed / Completed / Cancelled) |
| **Interactive Calendar** | Monthly calendar view with event dots, click-to-view details, and upcoming events list |
| **Menu Creator** | Create event-specific menus with per-plate pricing, category assignment, and bilingual names |
| **Team Management** | View and remove staff or manager accounts directly with automatic cascading data cleanup |
| **Task Management** | Dedicated `/assign-tasks/` page to assign, track, and manage team tasks with priority and deadlines |
| **Notes System** | Internal notes with role-based visibility — auto-deleted after 60 days, CSV download for admins |
| **Activity Logs** | Audit trail for manager actions with deep links to Calendar or Booking entries for quick review and approval |
| **Staff Tracker** | Track staff members, daily wages, advances, settlements, and generate financial graphs |
| **Bill Generator** | Printable invoices with cost breakdown, GST, and professional formatting |
| **Export System** | Export events and bookings as CSV/PDF with preview pages in light theme |
| **Gallery Manager** | Upload, reorder, and delete gallery images with Cloudinary CDN |
| **Login History** | Track login sessions with IP, device, browser, and timestamp |
| **User Management** | View all users, approve registrations via email, assign roles |

### 👔 Manager Dashboard

| Feature | Description |
|---------|-------------|
| **Event Coordination** | Create and edit events and bookings (financial data like staff wages is hidden) |
| **Menu Management** | Create and manage menus (unlocked only after admin approves the booking) — actions are auto-logged |
| **Assigned Tasks** | View tasks assigned by admin with accept/reject/complete workflow |
| **Personal Analytics** | Work summary chart showing personal activity over time |

### 👷 Staff Dashboard

| Feature | Description |
|---------|-------------|
| **Assigned Tasks** | View and respond to tasks (✓ complete / ✕ reject) assigned by admin |
| **Menu Viewer** | Preview menu PDFs in English and Gujarati (prices masked, download disabled, view-only in new tab) |
| **Calendar** | View events without pricing data (rates, costs masked as `**`) |
| **Personal Notes** | Create private notes visible only to themselves and admins |

### 👤 Customer View

| Feature | Description |
|---------|-------------|
| **Coming Soon** | Premium dark-themed "Under Development" page with business contact details |
| **No Access** | Customers cannot view dashboard, calendar, or any internal features |

---

## 🔐 Role-Based Access Control

```
┌─────────────────────────────────────────────────────────────────┐
│                        ADMIN (Full Access)                       │
│  Events · Menus · Bookings · Staff Tracker · Bills · Exports   │
│  Task Assignment · Notes (all) · Activity Logs · Gallery       │
│  User Management · Login History · All Analytics               │
├─────────────────────────────────────────────────────────────────┤
│                     MANAGER (Limited Access)                     │
│  Events · Menus · Bookings (no financial data)                 │
│  Own Tasks · Own Notes (visible to admin) · Calendar           │
│  Actions auto-logged for admin review                          │
├─────────────────────────────────────────────────────────────────┤
│                      STAFF (Minimal Access)                      │
│  Own Tasks · View-Only Menu · Calendar (no prices)             │
│  Own Notes (visible to admin)                                  │
├─────────────────────────────────────────────────────────────────┤
│                     CUSTOMER (No Access)                         │
│  "Coming Soon" page with contact details only                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.14 | Core language |
| Django | 6.0 | Web framework |
| Django REST Framework | 3.16.1 | REST API layer |
| Djoser | 2.3.3 | Auth endpoints (registration, login, token) |
| SimpleJWT | 5.5.1 | JWT token authentication |
| PostgreSQL | 16 | Primary database |
| Gunicorn | 23.0.0 | WSGI production server |
| WhiteNoise | 6.11.0 | Static file serving in production |
| Cloudinary | 1.44.1 | Cloud media storage and CDN |
| Anymail (Brevo) | 14.0 | Transactional email via Brevo API |
| Twilio | 9.9.0 | SMS/WhatsApp notifications (planned) |
| Pillow | 12.0.0 | Image processing |

### Frontend

| Technology | Purpose |
|-----------|---------|
| HTML5 | Semantic markup with SEO optimization |
| CSS3 | Custom properties, Flexbox, Grid, animations, media queries |
| JavaScript (ES6+) | DOM manipulation, Fetch API, dynamic rendering |
| Bootstrap 5 | Responsive grid and UI components |
| Django Templates | Server-side rendering with template inheritance |
| FullCalendar.js | Interactive calendar with event rendering |
| Chart.js | Analytics charts and financial graphs |
| Google Fonts | Playfair Display, Inter, Noto Sans Gujarati |

### Infrastructure

| Service | Purpose |
|---------|---------|
| AWS EC2 (Ubuntu) | Production server hosting |
| PostgreSQL | Database (self-hosted on EC2) |
| Nginx | Reverse proxy and SSL termination |
| Cloudinary | Media file CDN and image storage |
| Brevo (Sendinblue) | Transactional email delivery |
| GitHub | Version control and repository hosting |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
│  HTML / CSS / JS / Bootstrap · Django Templates · Fetch API      │
└──────────────────────────────┬───────────────────────────────────┘
                               │  HTTPS (Nginx + SSL)
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     DJANGO 6.0 APPLICATION                       │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐ │
│  │   Template Views     │  │       REST API (DRF 3.16)        │ │
│  │   (Server-Side)      │  │                                  │ │
│  │  • 30+ HTML pages    │  │  • Token Auth (Djoser)           │ │
│  │  • Component-based   │  │  • ViewSets + Custom Views       │ │
│  │  • Role-gated        │  │  • 35+ API endpoints             │ │
│  └──────────────────────┘  └──────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐ │
│  │   Signals & Hooks    │  │     Custom Auth Backend          │ │
│  │  • Admin approval    │  │  • Login via username, email,    │ │
│  │  • Welcome email     │  │    or phone number               │ │
│  │  • Activity logging  │  │  • Role-based permissions        │ │
│  └──────────────────────┘  └──────────────────────────────────┘ │
│                                                                  │
│  WhiteNoise · Gunicorn · CORS Headers · CSRF Protection          │
└──────┬──────────────────────────┬────────────────────┬───────────┘
       │                         │                     │
       ▼                         ▼                     ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  PostgreSQL  │       │  Cloudinary  │       │  Brevo SMTP  │
│  (AWS EC2)   │       │  (Media CDN) │       │  (Email API) │
│              │       │              │       │              │
│  20+ models  │       │  Profile     │       │  Admin       │
│  24 migra-   │       │  Category    │       │  alerts      │
│  tions       │       │  Food images │       │  Welcome     │
│              │       │              │       │  emails      │
└──────────────┘       └──────────────┘       └──────────────┘
```

---

## 🗄️ Database Schema

The platform uses **20 Django models** across the `catering` app:

| # | Model | Purpose |
|---|-------|---------|
| 1 | `User` | Custom user extending `AbstractUser` with roles, phone, profile image |
| 2 | `Category` | Menu categories with bilingual names and ordering |
| 3 | `Menu_item` | Individual menu items with English/Gujarati names and category FK |
| 4 | `Member` | Staff members for wage tracking |
| 5 | `MemberLog` | Daily wage/advance/settlement entries per member |
| 6 | `CateringEvent` | Full event records with date, guests, pricing, status, notes |
| 7 | `Menu` | Event-specific menus with selected items and per-plate rate |
| 8 | `Booking` | Customer booking submissions (name, phone, date, guests, type) |
| 9 | `GalleryItem` | Gallery images with title, ordering, and Cloudinary URLs |
| 10 | `MenuItemStats` | Usage statistics for menu items (for recommendations) |
| 11 | `ItemCoOccurrence` | Co-occurrence data for "Also Selected" recommendations |
| 12 | `EventStaff` | Staff assignment to events with roles and status |
| 13 | `Attendance` | Staff attendance tracking per event |
| 14 | `EventReminder` | Scheduled reminders for upcoming events |
| 15 | `TaskAssignment` | Admin-assigned tasks with priority, deadline, and status workflow |
| 16 | `UserLoginHistory` | Login session tracking with IP, device, and browser |
| 17 | `ActivityLog` | Audit trail for manager actions with deep-linking metadata |
| 18 | `AdminNote` | Role-scoped internal notes with auto-expiry |
| 19 | `PdfLog` | Tracking of PDF downloads and generation |

### Key Relationships

```
User ──┬── CateringEvent (creator)
       ├── TaskAssignment (assigned_by / assigned_to)
       ├── ActivityLog (user)
       ├── AdminNote (user)
       ├── UserLoginHistory (user)
       └── EventStaff (user)

CateringEvent ──┬── Menu (event)
                ├── EventStaff (event)
                ├── Attendance (event)
                └── EventReminder (event)

Category ── Menu_item (category)
Member ── MemberLog (member)
```

---

## 📡 API Reference

### Authentication (Djoser + Token Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/users/` | Register new user |
| POST | `/auth/token/login/` | Obtain auth token |
| POST | `/auth/token/logout/` | Invalidate token |
| GET | `/auth/users/me/` | Get current user profile |

### Core REST APIs (DRF Router)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/menu/categories/` | Menu categories CRUD |
| GET/POST | `/api/menu/menu-items/` | Menu items CRUD |
| GET/POST | `/api/menu/events/` | Catering events CRUD |
| GET/POST | `/api/menu/menus/` | Event menus CRUD |
| GET | `/api/menu/members/` | Staff members list |
| GET | `/api/menu/member-logs/` | Member wage logs |

### Custom API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/book-event/` | Submit booking request |
| GET/POST | `/api/tasks/` | List/create task assignments (`?my=true` for own tasks) |
| PATCH | `/api/tasks/<id>/status/` | Update task status |
| GET/POST | `/api/admin-notes/` | Internal notes with role-based visibility |
| GET | `/api/admin-notes/download/` | Download notes as CSV (admin only) |
| DELETE | `/api/admin-notes/<id>/delete/` | Delete a note |
| GET/POST | `/api/activity-logs/` | Manager activity audit trail |
| GET | `/api/staff-users/` | Staff/manager user list for task assignment |
| GET/POST | `/api/gallery/` | Gallery items list |
| POST | `/api/gallery/upload/` | Upload gallery image |
| DELETE | `/api/gallery/<id>/delete/` | Delete gallery image |
| GET | `/api/events/calendar/` | Calendar event data |
| PATCH | `/api/events/<id>/status/` | Update event status |
| POST | `/api/events/<id>/notes/` | Save internal notes on event |
| GET/POST | `/api/events/<id>/staff/` | Event staff assignment |
| GET | `/api/login-history/` | User login session history |
| POST | `/api/logout-all/` | Logout all active sessions |
| GET | `/api/menu/items/` | Public menu items (no auth) |
| GET | `/api/menu/recommend/` | AI menu recommendations |
| GET | `/api/menu/also-selected/<id>/` | "Also Selected" co-occurrence |
| POST | `/send-email/` | Contact form enquiry email |
| POST | `/api/log-pdf/` | Log PDF download event |
| GET | `/api/weather-suggest/` | Weather-based menu suggestions |

### Export Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/export/events/csv/` | Export events as CSV |
| GET | `/export/events/pdf/` | Export events as PDF |
| GET | `/export/bookings/csv/` | Export bookings as CSV |
| GET | `/export/bookings/pdf/` | Export bookings as PDF |

---

## 📁 Project Structure

```
Swagat_caterers/
├── README.md
├── LICENSE
├── .gitignore
│
└── backend/                          # Django project root
    ├── manage.py                     # Django CLI
    ├── Procfile                      # Railway: gunicorn backend_site.wsgi
    ├── requirements.txt              # 42 Python packages
    │
    ├── backend_site/                 # Django project configuration
    │   ├── settings.py               # DB, email, auth, CORS, security config
    │   ├── urls.py                   # Root URL routing (70+ routes)
    │   ├── views.py                  # User activation view
    │   ├── wsgi.py                   # Gunicorn WSGI entry point
    │   └── asgi.py                   # ASGI config
    │
    ├── catering/                     # Main Django app
    │   ├── models.py                 # 20 database models (512 lines)
    │   ├── views.py                  # 50+ views (1,225 lines)
    │   ├── serializers.py            # 15 DRF serializers
    │   ├── urls.py                   # App-level routing with DRF Router
    │   ├── admin.py                  # Custom admin with inlines & filters
    │   ├── signals.py                # Post-save email & notification hooks
    │   ├── backends.py               # Custom auth: email/phone/username login
    │   ├── exports.py                # CSV/PDF export views
    │   ├── chatbot.py                # AI chatbot for menu queries
    │   ├── decorators.py             # Custom permission decorators
    │   ├── validators.py             # Custom validation logic
    │   ├── context_processors.py     # Template context injection
    │   └── migrations/               # 24 migration files
    │
    ├── templates/                    # 30+ HTML templates
    │   ├── index.html                # Home page
    │   ├── menu.html                 # Public menu browsing
    │   ├── about.html                # About page
    │   ├── gallery.html              # Photo gallery
    │   ├── contact.html              # Contact page
    │   ├── booknow.html              # Booking form
    │   ├── customize_menu.html       # Custom menu builder (37KB)
    │   ├── calendar_public.html      # Public availability calendar
    │   ├── login.html                # Login page
    │   ├── signup.html               # Registration page
    │   ├── registration_pending.html # Admin approval pending notice
    │   ├── dashboard.html            # Main dashboard (104KB)
    │   ├── tracker.html              # Staff wage tracker (45KB)
    │   ├── booking.html              # Booking management
    │   ├── create_menu.html          # Menu creation tool (47KB)
    │   ├── direct_menu.html          # Direct menu viewer (39KB)
    │   ├── print_bill.html           # Invoice generation (25KB)
    │   ├── profile.html              # User profile management
    │   ├── assign_tasks.html         # Admin task assignment page
    │   ├── my_tasks.html             # User's assigned tasks
    │   ├── view_menu.html            # Staff read-only menu viewer
    │   ├── activity_review.html      # Admin activity audit page
    │   ├── gallery_manage.html       # Gallery management
    │   ├── login_history.html        # Login session history
    │   ├── export_events_preview.html    # Event export preview
    │   ├── export_bookings_preview.html  # Booking export preview
    │   ├── 404.html                  # Custom error page
    │   └── components/               # 28 reusable HTML components
    │       ├── navbar.html
    │       ├── footer.html
    │       ├── home_hero.html
    │       ├── pricing.html
    │       ├── testimonials.html
    │       ├── faq.html
    │       ├── gallery_grid.html
    │       └── ... (20+ more)
    │
    ├── static/
    │   ├── css/style.css             # Main stylesheet (black & gold theme)
    │   ├── js/
    │   │   ├── menu_data_en.js       # English menu data
    │   │   └── menu_data_gu.js       # Gujarati menu data
    │   ├── images/
    │   │   ├── logo/                 # Brand logo & favicon
    │   │   ├── food/                 # Food photography
    │   │   └── img/                  # General images
    │   └── Noto_Sans_Gujarati/       # Gujarati font family
    │
    ├── media/                        # User uploads (Cloudinary in prod)
    └── staticfiles/                  # Collected static (auto-generated)
```

---

## 📄 Pages & Templates

### Public Pages (No Authentication)

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Landing page with hero, packages, testimonials, stats |
| Menu | `/menu/` | Interactive menu browser with category filtering |
| About | `/about/` | Company story, team, and highlights |
| Gallery | `/gallery/` | Event and food photo showcase |
| Contact | `/contact/` | Contact form, WhatsApp, email, phone, map |
| Book Now | `/book-now/` | Multi-step event booking form |
| Calendar | `/calendar/` | Public availability calendar (supports `?date=` deep links) |
| Menu Builder | `/customize-menu/` | Custom menu creation with live pricing |
| Login | `/login/` | Email/phone/username authentication |
| Sign Up | `/signup/` | Registration with admin approval flow |

### Protected Pages (Login Required)

| Page | URL | Roles | Description |
|------|-----|-------|-------------|
| Dashboard | `/dashboard/` | All | Central hub — role-gated sections |
| Event Tracker | `/tracker/` | Admin | Staff wages, advances, settlements |
| Create Menu | `/direct-menu/` | Admin, Manager | Event menu builder |
| Print Bill | `/print-bill/` | Admin | Invoice generation and printing |
| Profile | `/profile/` | All | Profile image, email, phone editing |
| Booking | `/booking/` | Admin, Manager | Booking enquiry management |
| Assign Tasks | `/assign-tasks/` | Admin | Dedicated task assignment page |
| My Tasks | `/my-tasks/` | All | View assigned tasks, update status |
| View Menu | `/view-menu/` | Staff | Read-only menu in English & Gujarati |
| Activity Review | `/activity-review/` | Admin | Manager action audit with deep links |
| Gallery Manager | `/dashboard/gallery/` | Admin | Upload and manage gallery images |
| Login History | `/login-history/` | Admin | Session tracking and logout-all |
| Export Events | `/export/events/preview/` | Admin | Preview and export events |
| Export Bookings | `/export/bookings/preview/` | Admin | Preview and export bookings |

---

## 🔐 Authentication & Security

| Feature | Implementation |
|---------|---------------|
| **Authentication** | Token-based auth via Djoser + DRF TokenAuthentication |
| **Custom Backend** | `EmailPhoneUsernameBackend` — login with email, phone, or username |
| **Admin Approval** | New users are inactive by default; admin activates via email link |
| **CSRF Protection** | Django CSRF middleware enabled on all state-changing requests |
| **CORS** | `django-cors-headers` configured for allowed origins |
| **Role Gating** | All dashboard sections use client-side `user.user_type` checks + server-side `@login_required` and `@permission_classes` |
| **Password Hashing** | Django's PBKDF2 with SHA-256 (default) |
| **HTTPS** | Enforced via Railway SSL |
| **Session Security** | Login history tracking with IP, device, browser fingerprint |

---

## 📧 Email & Notification System

Powered by **Brevo (Sendinblue)** via `django-anymail`:

| Trigger | Recipient | Content |
|---------|-----------|---------|
| New user registration | Admin | Approval link to activate account |
| Account activated | User | Welcome email with login instructions |
| Booking submitted | Admin + User | Booking confirmation with event details |
| Task assigned | Staff/Manager | Task details, deadline, and priority |
| Contact form | Admin | Customer enquiry with details |

---

## 🌐 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Security
SECRET_KEY=your-django-secret-key
DEBUG=False

# Email (Brevo)
ANYMAIL_API_KEY=your-brevo-api-key
DEFAULT_FROM_EMAIL=your@email.com
ADMIN_EMAIL=admin@email.com

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Allowed Hosts
ALLOWED_HOSTS=your-domain.com,localhost
```

---

## 💻 Local Development Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Swagat_caterers.git
cd Swagat_caterers/backend

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database and API credentials

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Start development server
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

---

## 🚀 Deployment

### AWS EC2 (Production)

The project is deployed on an **AWS EC2 Ubuntu instance** with Nginx + Gunicorn:

- **Server:** Ubuntu 24.04 LTS on AWS EC2
- **Reverse Proxy:** Nginx with SSL
- **WSGI Server:** Gunicorn (`gunicorn backend_site.wsgi`)
- **Static files:** Served via WhiteNoise + Nginx
- **Database:** PostgreSQL (self-hosted on EC2)
- **Media:** Cloudinary CDN
- **Deployment:** `deploy.sh` script — pulls from GitHub, runs migrations, collects static, restarts Gunicorn
- **Environment:** All secrets via `.env` file on the server

### Production Checklist

- [x] `DEBUG = False`
- [x] `ALLOWED_HOSTS` configured
- [x] Nginx SSL with HTTPS redirect
- [x] Static files collected and served via WhiteNoise + Nginx
- [x] PostgreSQL as primary database
- [x] Cloudinary for media storage
- [x] Brevo for transactional email
- [x] CSRF and CORS properly configured
- [x] Gunicorn systemd service for auto-restart

---

## 📞 Contact & Author

<div align="center">

**Developed & Maintained by Preet Makadiya**

| Channel | Details |
|---------|---------|
| 📧 Email | [swagatcaterersofficial@gmail.com](mailto:swagatcaterersofficial@gmail.com) |
| 📱 Phone | [+91 81602 38745](tel:+918160238745) |
| 🌐 Website | [swagatcaterers.in](https://swagatcaterers.in) |
| 💼 GitHub | [makadiyapreet](https://github.com/makadiyapreet) |

</div>

---

## 📜 License

This project is **proprietary software**. All rights reserved.

© 2024–2026 Preet Makadiya & Swagat Caterers. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.

See [LICENSE](LICENSE) for full terms.
