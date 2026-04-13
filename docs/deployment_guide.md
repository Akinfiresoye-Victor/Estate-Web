# Estate Web — Hetzner VPS Deployment Guide
## Full Setup: Ubuntu 22.04 + Gunicorn + Nginx + GitHub Actions CI/CD

---

## Overview

This guide will take your Estate Web Django project from your local machine
to a live Hetzner VPS server, with automatic deployments every time you push
to GitHub. You won't need to SSH into the server to deploy updates — GitHub
Actions handles that automatically.

**What you'll have at the end:**
- Live site on your Namecheap domain (e.g. `estateweb.ng`)
- SSL certificate (HTTPS — the padlock in the browser)
- Auto-deploy: push to `main` branch → site updates in ~60 seconds
- Gunicorn serving Django, Nginx sitting in front of it
- PostgreSQL (Supabase) as your database

**Rough time to complete:** 2–4 hours if everything goes smoothly.

---

## PART 1 — Hetzner Server Setup

### Step 1.1 — Create Your Server

1. Go to [hetzner.com](https://hetzner.com) → Cloud → New Project → "Estate Web"
2. Click **Add Server**
3. Choose these settings:
   - **Location:** Falkenstein or Helsinki (closer to Nigeria than US servers)
   - **Image:** Ubuntu 22.04
   - **Type:** CX22 (2 vCPU, 4GB RAM) → ~€4.49/month. This is enough for launch.
   - **SSH Keys:** Add your SSH public key (explained below)
   - **Firewall:** Skip for now, we'll set it up manually
4. Click **Create & Buy**

**Getting your SSH public key (if you don't have one):**

Run this on your local machine (Windows PowerShell or Mac/Linux terminal):

```bash
ssh-keygen -t ed25519 -C "estateweb"
```

Press Enter through all prompts (use defaults). Then view your public key:

```bash
# On Mac/Linux:
cat ~/.ssh/id_ed25519.pub

# On Windows PowerShell:
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

Copy that entire line (starts with `ssh-ed25519 ...`) and paste it into
Hetzner's SSH key field.

---

### Step 1.2 — Connect to Your Server

Once Hetzner creates your server, you'll see an IP address (e.g. `49.12.34.56`).

```bash
ssh root@YOUR_SERVER_IP
```

Accept the fingerprint prompt by typing `yes`. You're now inside your server.

---

### Step 1.3 — Create a Deploy User

Running everything as `root` is dangerous. We create a dedicated user:

```bash
adduser deploy
```

Fill in a password when prompted. Then give it sudo (admin) access:

```bash
usermod -aG sudo deploy
```

Copy your SSH key to this user so you can log in as them:

```bash
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Test it — open a new terminal and try:

```bash
ssh deploy@YOUR_SERVER_IP
```

If it works, from now on use the `deploy` user, not `root`.

---

### Step 1.4 — System Updates and Required Packages

Log in as `deploy` and run:

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    python3 python3-pip python3-venv \
    nginx \
    git \
    curl \
    postgresql-client \
    build-essential \
    libpq-dev \
    python3-dev
```

**What each package does:**
- `python3-venv` — creates isolated Python environments (so your project's
  packages don't clash with system packages)
- `nginx` — the web server that sits in front of Django
- `postgresql-client` — tools to talk to your Supabase PostgreSQL database
- `libpq-dev` / `python3-dev` — needed to compile `psycopg2` (Django's
  PostgreSQL connector)

---

## PART 2 — Project Setup on the Server

### Step 2.1 — Clone Your Repository

```bash
cd /home/deploy
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git estateweb
cd estateweb
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub details.

---

### Step 2.2 — Create Python Virtual Environment

A virtual environment is like a clean, isolated box for your project's
Python packages. It means the packages you install here don't affect
anything else on the server.

```bash
cd /home/deploy/estateweb
python3 -m venv venv
source venv/bin/activate
```

After running `source venv/bin/activate`, your terminal prompt changes
to show `(venv)` at the start. That means the virtual environment is active.

Install your project's dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

---

### Step 2.3 — Create Your .env File

Your Django project needs environment variables (secret settings that should
never go in your Git repository). Create the file on the server:

```bash
nano /home/deploy/estateweb/.env
```

Paste in your environment variables. Here's the template — fill in your
actual values:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_SERVER_IP

# Supabase PostgreSQL connection
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres

# Or individual DB settings if you use them separately:
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-password
DB_HOST=db.YOUR_PROJECT.supabase.co
DB_PORT=5432

# Email (when you set it up)
# EMAIL_HOST=smtp-relay.brevo.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=your@email.com
# EMAIL_HOST_PASSWORD=your-brevo-key
```

Save with `Ctrl+O`, Enter, then `Ctrl+X` to exit nano.

**Important:** Make sure your Django `settings.py` reads from environment
variables (using `os.environ.get(...)` or the `python-dotenv` package).

---

### Step 2.4 — Django Setup Commands

```bash
cd /home/deploy/estateweb
source venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

**What `collectstatic` does:** Django in production mode (`DEBUG=False`)
doesn't serve your CSS/JS/images directly. `collectstatic` copies all static
files into one folder (`/static/`) that Nginx will serve instead. This is
much faster.

---

### Step 2.5 — Test Gunicorn Works

Before setting up the automatic service, test it manually:

```bash
cd /home/deploy/estateweb
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 your_project_name.wsgi:application
```

Replace `your_project_name` with your actual Django project folder name
(the folder that contains `settings.py`, `wsgi.py`, `urls.py`).

If you see `[INFO] Listening at: http://0.0.0.0:8000` — it works. Press
`Ctrl+C` to stop it.

---

## PART 3 — Gunicorn as a System Service

We want Gunicorn to start automatically when the server boots, and restart
if it crashes. We use `systemd` (Ubuntu's service manager) for this.

### Step 3.1 — Create the Gunicorn Socket File

A "socket" is like a pipe between Nginx and Gunicorn — Nginx passes requests
through the socket to Gunicorn. This is faster than using a port number.

```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

Paste this:

```ini
[Unit]
Description=Gunicorn socket for Estate Web

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Save and exit (`Ctrl+O`, Enter, `Ctrl+X`).

---

### Step 3.2 — Create the Gunicorn Service File

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste this (replace `your_project_name` with your Django project folder name):

```ini
[Unit]
Description=Gunicorn daemon for Estate Web
Requires=gunicorn.socket
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/home/deploy/estateweb
EnvironmentFile=/home/deploy/estateweb/.env
ExecStart=/home/deploy/estateweb/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          your_project_name.wsgi:application

[Install]
WantedBy=multi-user.target
```

**What `--workers 3` means:** Gunicorn runs 3 worker processes. Each worker
can handle one request at a time. 3 workers means you can handle 3 simultaneous
requests. For a fresh launch with moderate traffic, this is fine.

Save and exit.

---

### Step 3.3 — Enable and Start Gunicorn

```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

Test that the socket was created:

```bash
sudo systemctl status gunicorn.socket
```

You should see `active (listening)`. Now trigger it:

```bash
curl --unix-socket /run/gunicorn.sock localhost
```

You should get HTML back. Then check the service status:

```bash
sudo systemctl status gunicorn
```

---

## PART 4 — Nginx Configuration

Nginx is the "front door" of your server. It receives all incoming web
traffic and passes it to Gunicorn through the socket.

### Step 4.1 — Create Nginx Config for Estate Web

```bash
sudo nano /etc/nginx/sites-available/estateweb
```

Paste this (replace `your-domain.com` with your actual domain):

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Where your static files are collected to
    location /static/ {
        alias /home/deploy/estateweb/staticfiles/;
    }

    # Where uploaded media files are (if you have file uploads)
    location /media/ {
        alias /home/deploy/estateweb/media/;
    }

    # Everything else goes to Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

**Note:** The `/static/` path should match your `STATIC_ROOT` setting in
Django. If you set `STATIC_ROOT = BASE_DIR / 'staticfiles'`, the alias
above is correct. Adjust if yours is different.

---

### Step 4.2 — Enable the Site

```bash
# Create a symlink (shortcut) to enable the site
sudo ln -s /etc/nginx/sites-available/estateweb /etc/nginx/sites-enabled/

# Remove the default Nginx page
sudo rm /etc/nginx/sites-enabled/default

# Test that Nginx config has no errors
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

### Step 4.3 — Configure Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

`ufw` is Ubuntu's firewall. We allow Nginx (ports 80 and 443) and SSH
(port 22). Everything else is blocked.

At this point, visiting `http://YOUR_SERVER_IP` in a browser should show
your Django site (without HTTPS yet).

---

## PART 5 — Domain and SSL

### Step 5.1 — Point Your Namecheap Domain to Hetzner

In Namecheap's DNS settings for your domain, add these A records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A    | @    | YOUR_SERVER_IP | Auto |
| A    | www  | YOUR_SERVER_IP | Auto |

DNS changes can take anywhere from a few minutes to 48 hours to propagate
(spread across the internet). Usually it's under an hour.

---

### Step 5.2 — Install SSL with Certbot

Certbot is a free tool that gets you an SSL certificate from Let's Encrypt.
SSL is what makes your site `https://` instead of `http://`.

```bash
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts:
- Enter your email address
- Agree to terms
- Choose whether to share email with EFF (your choice)

Certbot will automatically update your Nginx config to handle HTTPS.

**Auto-renewal:** Certbot automatically renews certificates before they
expire. Test that auto-renewal works:

```bash
sudo certbot renew --dry-run
```

---

## PART 6 — GitHub Actions Auto-Deploy

This is the part that makes deployment magical. Every time you push code
to your `main` branch on GitHub, GitHub Actions will SSH into your server
and update the live site automatically.

### Step 6.1 — Create a Deploy SSH Key

On your **local machine** (not the server), create a dedicated key pair
just for deployments:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy
```

This creates two files:
- `github_actions_deploy` — the private key (GitHub Actions will use this)
- `github_actions_deploy.pub` — the public key (the server will have this)

---

### Step 6.2 — Add the Public Key to Your Server

Copy the public key content:

```bash
cat ~/.ssh/github_actions_deploy.pub
```

Then on your server, add it to the deploy user's authorized keys:

```bash
# On the server:
nano /home/deploy/.ssh/authorized_keys
```

Paste the public key on a new line. Save and exit.

---

### Step 6.3 — Add Secrets to GitHub

In your GitHub repository, go to:
**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets one by one:

| Secret Name | Value |
|-------------|-------|
| `HETZNER_HOST` | Your server IP (e.g. `49.12.34.56`) |
| `HETZNER_USER` | `deploy` |
| `HETZNER_SSH_KEY` | The **private** key content (from `cat ~/.ssh/github_actions_deploy`) |
| `HETZNER_PORT` | `22` |

For `HETZNER_SSH_KEY`, copy the entire content of the private key file,
including the `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines.

---

### Step 6.4 — Create the GitHub Actions Workflow File

In your project on your **local machine**, create this folder structure:

```
your-project/
  .github/
    workflows/
      deploy.yml
```

Create the file `.github/workflows/deploy.yml`:

```yaml
name: Deploy Estate Web to Hetzner

on:
  push:
    branches:
      - main   # Only runs when you push to 'main' branch

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Hetzner VPS
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HETZNER_HOST }}
          username: ${{ secrets.HETZNER_USER }}
          key: ${{ secrets.HETZNER_SSH_KEY }}
          port: ${{ secrets.HETZNER_PORT }}
          script: |
            # Go to project directory
            cd /home/deploy/estateweb

            # Pull latest code from GitHub
            git pull origin main

            # Activate virtual environment
            source venv/bin/activate

            # Install any new dependencies
            pip install -r requirements.txt

            # Apply any new database migrations
            python manage.py migrate --noinput

            # Collect static files
            python manage.py collectstatic --noinput

            # Restart Gunicorn to load new code
            sudo systemctl restart gunicorn

            echo "Deployment complete!"
```

**What this workflow does, step by step:**
1. Triggers whenever you push to the `main` branch
2. GitHub spins up a temporary Ubuntu machine
3. It SSHes into your Hetzner server using the secrets you added
4. On the server, it pulls new code, installs new packages, runs migrations,
   collects static files, and restarts Gunicorn
5. Your site is now running the new code

---

### Step 6.5 — Allow Deploy User to Restart Gunicorn Without Password

By default, `sudo` commands require a password. But GitHub Actions can't type
a password. We need to allow the `deploy` user to restart Gunicorn without one.

On the server:

```bash
sudo visudo
```

This opens the sudoers file safely. Add this line at the **bottom**:

```
deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart gunicorn
```

Save and exit (in nano: `Ctrl+O`, Enter, `Ctrl+X`).

---

### Step 6.6 — Push and Test

Commit your workflow file and push to GitHub:

```bash
git add .github/
git commit -m "Add GitHub Actions deployment workflow"
git push origin main
```

Then go to your GitHub repository → **Actions** tab. You'll see the workflow
running. Click on it to watch the logs in real time.

If it shows a green checkmark ✅ — your deployment pipeline is working!

---

## PART 7 — Maintenance and Troubleshooting

### Checking logs when something breaks

```bash
# Gunicorn logs (your Django errors will appear here)
sudo journalctl -u gunicorn --no-pager -n 50

# Nginx access logs (every request)
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Restarting services manually

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Making a manual deployment (SSH in and run it yourself)

```bash
ssh deploy@YOUR_SERVER_IP
cd /home/deploy/estateweb
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### If the site shows 502 Bad Gateway

This means Nginx can't reach Gunicorn. Check Gunicorn:

```bash
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 30
```

### If static files (CSS/images) aren't loading

Make sure:
1. `python manage.py collectstatic` ran successfully
2. The `STATIC_ROOT` path in `settings.py` matches the `alias` in your Nginx config
3. The `deploy` user owns the files: `ls -la /home/deploy/estateweb/staticfiles/`

### If GitHub Actions fails at the "restart gunicorn" step

Make sure the sudoers line was added correctly:

```bash
sudo visudo -c   # Check for syntax errors in sudoers
sudo cat /etc/sudoers | grep deploy
```

---

## PART 8 — Your settings.py Checklist

Before going live, confirm these are correct in `settings.py`:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Read from environment
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # Where collectstatic puts files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = True              # Redirect HTTP to HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000         # Tell browsers to always use HTTPS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

---

## Summary — What You've Built

```
Internet
   ↓
Nginx (port 443, handles HTTPS, serves static files)
   ↓ (passes dynamic requests)
Gunicorn (runs Django application, 3 workers)
   ↓
Django (your Estate Web code)
   ↓
Supabase PostgreSQL (your database)
```

**Auto-deploy flow:**
```
You push to GitHub main branch
   ↓
GitHub Actions triggers
   ↓
GitHub SSHes into Hetzner server
   ↓
Pulls new code, runs migrations, collects static files
   ↓
Restarts Gunicorn
   ↓
Users see updated site (~60 seconds total)
```

---

*Estate Web — Deployment Guide v1.0*