# Estate Web - Real Estate Management Platform

## Overview

Estate Web is a comprehensive Django-based web application designed for real estate professionals, property owners, real estate companies, and individual agents. The platform facilitates property listing (for lease and sale), lead management, appointment scheduling, company/team management, analytics, and administrative oversight. It supports multi-user roles including super admins, company admins, agents, and general users.

Key features include responsive dashboards for agents and companies, property management with image uploads via Cloudinary, WhatsApp integration for leads, job posting/recruitment, feedback systems, and advanced analytics (views, rankings, ratings).

The project is production-ready with PostgreSQL support, Cloudinary media storage, Whitenoise for static files, and deployment configurations for platforms like Render/ Railway.

## Project Structure

```
Estate Web/
├── estate_web/          # Main Django project settings and URLs
├── admin_panel/         # Admin dashboard for superusers (feedback, analytics)
├── agents/              # Agent management (profiles, dashboards, leads)
├── companies/           # Company management (teams, jobs, analytics)
├── core/                # Core utilities (models, views, feedback, scraping)
├── estate/              # Property listings (rentals, sales)
├── members/             # Custom user authentication (profiles, social links)
├── media/               # User-uploaded files (local dev)
├── static/              # Collected static files
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── Procfile             # Heroku/Render deployment
└── README.md            # This file
```

## Technology Stack

- **Backend**: Django 5.x, PostgreSQL (production), SQLite (dev)
- **Frontend**: Bootstrap 5, custom responsive CSS, Django templates
- **Media**: Cloudinary (production), local filesystem (dev)
- **Static Files**: Whitenoise (compressed CDN)
- **Third-party**: django-allauth (auth), django-widget-tweaks, django-filters, Pillow
- **Deployment**: Render/Railway/Heroku (Procfile + dj-database-url)
- **Other**: WhatsApp API integration, news scraping (BeautifulSoup)

## Features

### 1. **Property Management**
   - List properties for lease/sale with multiple images
   - Price ranges, locations, commercial/residential filters
   - Wishlists, property views tracking
   - Owner/agent assignment

### 2. **User Roles & Dashboards**
   - **Agents**: Profile setup (headshot, WhatsApp), leads inbox, analytics (rankings, commissions), portfolio
   - **Companies**: Team management, job postings/applications, company verification (KYC), activity logs
   - **Responsive**: Mobile-first design, bottom nav, FAB menus

### 3. **Lead & CRM**
   - Inquiry tracking with WhatsApp one-tap messaging
   - Recent leads display, new lead badges
   - Appointment scheduling (virtual/personal/business)

### 4. **Analytics & Progress**
   - Market ranking, average views, ratings/reviews
   - Profile completion checklists (missions system)
   - Commission estimates from active listings

### 5. **Admin Panel**
   - Superuser dashboard
   - Feedback management
   - Company/activity oversight

### 6. **Company Operations**
   - Job postings with applicant tracking
   - Agent invitations
   - Social media links, contact info
   - Verified badges (logo, KYC, agents)

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ (production)
- Node.js (optional, for asset compilation)
- Cloudinary account (recommended for production images)

## Quick Start (Development)

1. **Clone & Virtual Environment**
   ```
   git clone <repo-url>
   cd "Estate Web"
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Environment Setup** (`.env` file)
   ```
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   DB_NAME=estate_db
   DB_USER=your_pg_user
   DB_PASSWORD=your_pg_pass
   DB_HOST=localhost
   DB_PORT=5432
   ALLOWED_HOSTS=localhost,127.0.0.1
   USE_CLOUDINARY=False  # True for prod
   ```

4. **Database & Migrations**
   ```
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Collect Static & Run**
   ```
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000`

## Production Deployment (Render/Railway)

1. **Environment Variables** (Platform Dashboard)
   ```
   SECRET_KEY=...
   DEBUG=False
   DJANGO_DATABASE_URL=postgresql://user:pass@host:port/dbname
   ALLOWED_HOSTS=yourdomain.com,*.onrender.com
   USE_CLOUDINARY=True
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   ```

2. **Build/Start Commands**
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `gunicorn estate_web.wsgi:application`

3. **Deploy**: Push to Git, auto-deploys via webhook.

## Database Models (Key)

| App | Models |
|-----|--------|
| `estate` | PropertyManagementRent, PropertyManagementSale, SalePropertyImage |
| `agents` | AgentInformation, AgentAnalytics, AgentRating, SocialLinks |
| `companies` | CompanyInformation, CompanyAnalytics, JobPost, CompanyActivityLog |
| `core` | Appointments, Feedbacks, PropertyViews |
| `members` | User (custom auth) |

## Custom Management Commands

- `news_scrape` (core): Scrapes real estate news
- Standard Django: `runserver`, `migrate`, `createsuperuser`

## API Integrations

- **WhatsApp**: One-tap lead messaging (`wa.me/` links)
- **Cloudinary**: Image optimization/CDN
- **Google Fonts/BootstrapCDN**: UI assets

## Customization

### Templates
Extend base templates:
- Agents: `agents/templates/agent/base.html`
- Companies: `companies/templates/company/base.html`
- Core: `core/templates/core/base.html`

### Static Files
```
static/agent/css/dashboard.css     # Agent dashboard
static/company/css/dashboard.css   # Company dashboard
static/admin_panel/css/feedback_view.css  # Admin UI
```

### Settings Overrides
- `USE_CLOUDINARY=True` → Production media
- `USE_DB=False` → SQLite dev mode

## Migrations History

Over 50 migrations across apps, handling:
- UUID fields (appointments, leads)
- Image handling (Pillow/Cloudinary)
- Analytics tracking
- Custom user fields

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Security

- CSRF protection enabled
- Custom `AUTH_USER_MODEL`
- Password validators
- Allowed hosts via env
- Production: HTTPS enforced via CSRF_TRUSTED_ORIGINS

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No module named 'psycopg2'` | `pip install psycopg2-binary` |
| Static files 404 | `python manage.py collectstatic` |
| Cloudinary errors | Check API keys/env vars |
| Migrations conflict | `python manage.py makemigrations --merge` |
| WhatsApp links fail | Verify phone format (234XXXXXXXXX) |

## License

MIT License - see LICENSE file for details.

## Contact

For support: Contact project maintainer via GitHub Issues.
