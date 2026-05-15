# SubTrack — Subscription Tracker & Optimizer

A production-quality Django web application for tracking subscriptions, monitoring recurring payments, receiving renewal reminders, analyzing spending, and detecting subscriptions from Gmail emails.

## Features

- **Subscription Management**: Add, edit, pause, cancel, and delete subscriptions
- **Analytics Dashboard**: Beautiful charts showing spending trends, category breakdowns, and yearly projections
- **Renewal Alerts**: Automated reminders via Celery before subscriptions renew
- **Gmail Detection**: Scan Gmail inbox for subscription receipts using regex-based parsing
- **Free Trial Tracking**: Monitor trial periods and get alerts before conversion
- **Export Reports**: Download subscription data as CSV or PDF
- **Google OAuth**: Secure login with Google account
- **Responsive Design**: Works on desktop, tablet, and mobile

## Tech Stack

- **Backend**: Django 5.0, Django ORM, Celery, Redis
- **Frontend**: Django Templates, Tailwind CSS, Chart.js, Lucide Icons
- **Database**: PostgreSQL
- **APIs**: Gmail API, Google OAuth 2.0
- **Deployment**: Render-ready with Gunicorn, WhiteNoise

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd subtrack
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb subtrack
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create categories**
   ```bash
   python manage.py loaddata categories
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` in your browser.

### Celery Setup (for scheduled tasks)

Start Redis server, then:

```bash
# Terminal 1: Start Celery worker
celery -A core worker --loglevel=info

# Terminal 2: Start Celery beat (scheduler)
celery -A core beat --loglevel=info
```

## Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:8000/accounts/auth/google/callback/`
6. Copy Client ID and Client Secret to your `.env` file

## Deployment

### Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables from `.env.example`
4. Render will use `render.yaml` or the `Procfile` automatically

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `DATABASE_URL` | PostgreSQL connection URL | Yes |
| `REDIS_URL` | Redis connection URL | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | For Gmail |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | For Gmail |
| `EMAIL_HOST_USER` | SMTP email address | For emails |
| `EMAIL_HOST_PASSWORD` | SMTP app password | For emails |

## Project Structure

```
subtrack/
├── accounts/           # User authentication & profiles
├── dashboard/          # Main dashboard views
├── subscriptions/      # Subscription CRUD & management
├── analytics_app/      # Analytics & reporting utilities
├── gmail_detection/    # Gmail scanning & detection
├── notifications/      # In-app notifications
├── reports/            # CSV/PDF export
├── core/               # Django settings & configuration
├── templates/          # All HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploads
├── requirements.txt
├── manage.py
└── .env.example
```

## License

MIT License
