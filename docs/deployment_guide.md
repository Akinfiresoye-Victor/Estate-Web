# Estate Web — Complete VPS Deployment Guide
### Django + PostgreSQL + Gunicorn + Nginx + HTTPS + Email
> Written for intermediate Python developers who are new to DevOps.
> Every step explains the *why*, not just the *what*.

---

## Before You Start — Hosting Options Explained

### Should You Use a VPS or a Free Platform?

This is one of the most important decisions for your project. Let's break it down honestly.

---

### Option A: Free/Cheap Platforms (Vercel, Supabase, Render, Railway)

| Platform | What It Does | Free Tier | Django Friendly? |
|---|---|---|---|
| **Vercel** | Hosts frontend/serverless functions | Yes | ❌ Not for Django |
| **Supabase** | Managed PostgreSQL database only | Yes (limited) | ✅ For DB only |
| **Render** | Hosts Django apps + PostgreSQL | Yes (sleeps after 15min) | ✅ Yes |
| **Railway** | Hosts Django + DB together | $5/month credit | ✅ Yes |
| **PythonAnywhere** | Beginner-friendly Django hosting | Yes (limited) | ✅ Yes |

**The Risk You Heard About** — Hosting an entire app on one *free* platform means:
- If that platform has downtime, your app goes down completely.
- Free tiers spin down when inactive (Render free tier sleeps — users get a 30-second wait).
- You lose control over server configuration, environment, and performance.

**Recommended Strategy for You Right Now:**

Since Estate Web is in early stage (2025–2026 phase), here is the smart path:

```
Phase 1 (Now → First 100 users): Use Render FREE + Supabase FREE
Phase 2 (First revenue):         Move to a cheap VPS ($5–$6/month)
Phase 3 (Growth):                Upgrade VPS or use managed hosting
```

**Why Render + Supabase for now?**
- Render hosts your Django app for free (with sleep limitation).
- Supabase gives you a real PostgreSQL database for free.
- You focus on building features, not managing servers.
- Zero cost while you're still getting traction.

---

### Best Free/Cheap Hosting Combinations

#### 🥇 Best Free Combo: Render + Supabase
- **Render** → Hosts your Django app (free, sleeps after 15 min idle)
- **Supabase** → Free PostgreSQL database (500MB, plenty for early stage)
- **Cloudflare** → Free CDN + DNS management + free SSL
- **Total cost: ₦0/month**

#### 🥈 Best Paid Starter: Railway (~$5/month)
- Hosts Django + PostgreSQL together
- Doesn't sleep. Always on.
- Simple GitHub deploy pipeline
- **Total cost: ~₦7,500/month**

#### 🥉 Full Control VPS: Hetzner / DigitalOcean / Vultr
- Hetzner CX11 (Germany): **€3.29/month** (~₦5,000) — best value in the world
- DigitalOcean Droplet: **$4/month** (~₦6,000)
- Vultr: **$2.50/month** (~₦4,000) — cheapest
- **You get full server control. This guide covers this path.**

---

> **My Recommendation for You:** Start on **Render (free) + Supabase (free)** today.
> Follow this VPS guide when you have your first paying users or ₦5,000/month budget.
> The VPS guide below uses **Hetzner** (cheapest and reliable).

---

## Part 1 — The VPS Deployment Guide (Full Production Setup)

### What We're Building

```
Your Users (Browser/Phone)
        ↓ HTTPS (port 443)
    [Nginx] ← Reverse Proxy (the "gatekeeper")
        ↓ HTTP (internal, port 8000)
   [Gunicorn] ← Application Server (runs Django)
        ↓
    [Django] ← Your actual web app
        ↓
  [PostgreSQL] ← Database (stores all data)
```

**Plain English Explanation of Each Layer:**
- **Nginx** = The bouncer at the door. It receives all web traffic and decides where to send it.
- **Gunicorn** = The actual worker. It runs your Django app and handles multiple users at once.
- **Django** = Your code. Business logic, views, models — everything you wrote.
- **PostgreSQL** = The database where properties, users, agents are stored.

---

## Step 1 — Get Your VPS (Server)

### Where to Buy

Go to **[Hetzner Cloud](https://www.hetzner.com/cloud)** (cheapest reliable option):
1. Create an account
2. Create a new project
3. Create a Server:
   - **Location:** Helsinki or Nuremberg (fastest to Nigeria surprisingly)
   - **Image:** Ubuntu 22.04
   - **Type:** CX11 (2GB RAM, 1 CPU) — plenty for Estate Web early stage
   - **SSH Key:** Generate one (covered below)

### Generate an SSH Key (on YOUR laptop/PC)

SSH is how you connect to your server securely — like a password, but more secure.

**On Windows (PowerShell or Git Bash):**
```bash
ssh-keygen -t ed25519 -C "estateweb@yourmail.com"
```

**On Mac/Linux:**
```bash
ssh-keygen -t ed25519 -C "estateweb@yourmail.com"
```

When asked where to save: press Enter (saves to `~/.ssh/id_ed25519`).
When asked for passphrase: choose one or leave empty.

**Get your public key to paste into Hetzner:**
```bash
cat ~/.ssh/id_ed25519.pub
```
Copy that output and paste it when Hetzner asks for your SSH key.

---

## Step 2 — First Login & Initial Server Setup

### Connect to Your Server

```bash
ssh root@YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with the IP address Hetzner gives you (e.g., `65.21.150.44`).

You should see a terminal prompt like `root@ubuntu-2gb-hel1-1:~#`

---

### 2A — Update the Server

**WHY:** Your server comes with software that may be months old. Running updates closes security holes.

```bash
apt update && apt upgrade -y
```

- `apt update` = Fetches the latest list of available software versions.
- `apt upgrade -y` = Installs the newer versions. `-y` means "yes to all prompts."

---

### 2B — Create a Non-Root User

**WHY:** The `root` user has unlimited power — if someone hacks in as root, they own your server. A regular user with `sudo` (limited root power) is much safer.

```bash
adduser estateadmin
```

You'll be asked to set a password. Choose a strong one. Skip the other questions with Enter.

**Give this user sudo power (ability to run admin commands):**
```bash
usermod -aG sudo estateadmin
```

`-aG sudo` means "add to the sudo group."

**Copy your SSH key to the new user so you can log in as them:**
```bash
rsync --archive --chown=estateadmin:estateadmin ~/.ssh /home/estateadmin
```

This copies the `~/.ssh` folder (with your authorized keys) to the new user's home directory.

**Test this before you lock out root:**
```bash
# Open a NEW terminal window and try:
ssh estateadmin@YOUR_SERVER_IP
```

If it works, great. If not, DO NOT close the root session yet — fix it first.

---

### 2C — Configure the Firewall

**WHY:** By default, all ports on your server are open. That's like leaving every door and window in your house open. We only want to allow traffic on specific ports.

```bash
ufw allow OpenSSH        # Port 22 — for you to log in via SSH
ufw allow 'Nginx Full'   # Port 80 (HTTP) and 443 (HTTPS) — for web traffic
ufw enable               # Turn the firewall on
ufw status               # Confirm it's working
```

You should see this output:
```
Status: active
To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

---

### 2D — Disable Root Login (Important Security Step)

**WHY:** Hackers constantly try to brute-force the `root` user. If you disable root login via SSH, they can't even try.

```bash
nano /etc/ssh/sshd_config
```

Find this line:
```
PermitRootLogin yes
```

Change it to:
```
PermitRootLogin no
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

Restart SSH to apply the change:
```bash
systemctl restart sshd
```

**⚠ WARNING:** Make sure you can log in as `estateadmin` before doing this. Test in a separate terminal first.

---

## Step 3 — Install Python, pip, and Virtualenv

**From now on, log in as `estateadmin`:**
```bash
ssh estateadmin@YOUR_SERVER_IP
```

### Install Python

Ubuntu 22.04 comes with Python 3.10. Check it:
```bash
python3 --version
```

Install pip (Python's package manager) and virtualenv:
```bash
sudo apt install python3-pip python3-venv python3-dev -y
```

- `python3-pip` = Tool to install Python packages.
- `python3-venv` = Creates isolated Python environments (so packages don't conflict).
- `python3-dev` = Python header files needed to compile some packages like `psycopg2`.

---

## Step 4 — Install and Configure PostgreSQL

**WHY PostgreSQL instead of SQLite?**
SQLite is a file-based database — great for development and testing on your laptop. But on a production server with multiple users hitting your site at once, SQLite can get corrupted or locked. PostgreSQL is built for this — it handles many users simultaneously.

### Install PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
```

- `postgresql` = The actual database software.
- `postgresql-contrib` = Extra tools and extensions.

### Start and Enable PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Makes it auto-start when server reboots
```

### Create a Database and User for Estate Web

```bash
sudo -u postgres psql
```

This logs you into PostgreSQL as the `postgres` superuser. Your prompt changes to `postgres=#`.

Now run these SQL commands:

```sql
CREATE DATABASE estateweb_db;
CREATE USER estateweb_user WITH PASSWORD 'your_strong_password_here';
ALTER ROLE estateweb_user SET client_encoding TO 'utf8';
ALTER ROLE estateweb_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE estateweb_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE estateweb_db TO estateweb_user;
\q
```

**What each line does:**
- `CREATE DATABASE` = Creates your database called `estateweb_db`.
- `CREATE USER` = Creates a database user (not a Linux user — different thing).
- `ALTER ROLE ... SET` = Performance and encoding settings Django recommends.
- `GRANT ALL PRIVILEGES` = Gives your user full access to the database.
- `\q` = Quit PostgreSQL.

**⚠ IMPORTANT:** Replace `your_strong_password_here` with a real password. Save it somewhere safe.

---

## Step 5 — Clone Your Django Project

### Install Git

```bash
sudo apt install git -y
```

### Create a Directory for Your App

```bash
sudo mkdir -p /var/www/estateweb
sudo chown estateadmin:estateadmin /var/www/estateweb
```

- `/var/www/` = Traditional location for web apps on Linux.
- `chown` = Changes the owner of that folder to your `estateadmin` user.

### Clone From GitHub

```bash
cd /var/www/estateweb
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .
```

The `.` at the end means "clone into this current folder, not a subfolder."

---

## Step 6 — Set Up Virtual Environment and Install Dependencies

```bash
cd /var/www/estateweb
python3 -m venv venv
```

This creates a folder called `venv/` — your isolated Python environment.

**Activate it:**
```bash
source venv/bin/activate
```

Your prompt will change to `(venv) estateadmin@...` — this means the virtual environment is active.

**Install your project dependencies:**
```bash
pip install -r requirements.txt
```

**Make sure these are in your requirements.txt:**
```
django
gunicorn
psycopg2-binary
python-decouple
whitenoise
```

- `gunicorn` = The production application server.
- `psycopg2-binary` = Lets Django talk to PostgreSQL.
- `python-decouple` = Manages environment variables from a `.env` file.
- `whitenoise` = Serves your static files (CSS, JS) efficiently without Nginx involvement.

---

## Step 7 — Configure Environment Variables Securely

**WHY `.env` files?**
Your `settings.py` should NEVER have your database password, secret key, or email credentials written directly in it. If you push to GitHub, the world can see them. An `.env` file keeps secrets out of your code.

### Create the `.env` File

```bash
nano /var/www/estateweb/.env
```

Paste this (fill in your actual values):

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_SERVER_IP

# PostgreSQL
DB_NAME=estateweb_db
DB_USER=estateweb_user
DB_PASSWORD=your_strong_password_here
DB_HOST=localhost
DB_PORT=5432

# Email (Brevo or Postmark — fill in later)
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_brevo_login@email.com
EMAIL_HOST_PASSWORD=your_brevo_smtp_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

Save with `Ctrl+X`, `Y`, `Enter`.

**Lock down the file permissions so only your user can read it:**
```bash
chmod 600 /var/www/estateweb/.env
```

`600` means: owner can read and write, nobody else can do anything.

### Update `settings.py` to Use `.env`

In your `settings.py`, use `python-decouple`:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
```

**Add Whitenoise for static files (in settings.py):**

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this right after SecurityMiddleware
    # ... rest of middleware
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## Step 8 — Run Migrations and Collect Static Files

Make sure your virtual environment is active:

```bash
cd /var/www/estateweb
source venv/bin/activate
```

**Run migrations** (creates all your database tables):
```bash
python manage.py migrate
```

**Create a superuser** (your admin account):
```bash
python manage.py createsuperuser
```

**Collect static files** (copies all CSS, JS, images to one folder Nginx can serve):
```bash
python manage.py collectstatic --noinput
```

This creates a `staticfiles/` folder with everything in it.

---

## Step 9 — Set Up Gunicorn

**WHY Gunicorn?**
Django's built-in server (`python manage.py runserver`) is only for development — it can only handle one request at a time and is not secure. Gunicorn is a production-grade server that can handle many users simultaneously.

### Test Gunicorn Manually First

```bash
cd /var/www/estateweb
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 estateweb.wsgi:application
```

Replace `estateweb` with your Django project name (the folder that has `wsgi.py` inside it).

If you see `[INFO] Listening at: http://0.0.0.0:8000` — it works! Press `Ctrl+C` to stop it.

### Create a Gunicorn Systemd Service

**WHY systemd?** You don't want to manually start Gunicorn every time the server reboots. Systemd is Linux's service manager — it starts, stops, and automatically restarts services.

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste this:

```ini
[Unit]
Description=Gunicorn daemon for Estate Web
After=network.target

[Service]
User=estateadmin
Group=www-data
WorkingDirectory=/var/www/estateweb
EnvironmentFile=/var/www/estateweb/.env
ExecStart=/var/www/estateweb/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/estateweb/gunicorn.sock \
          estateweb.wsgi:application

[Install]
WantedBy=multi-user.target
```

**What each part means:**
- `After=network.target` = Only start after the network is available.
- `User=estateadmin` = Run as your user (not root — safer).
- `EnvironmentFile` = Load your `.env` variables.
- `--workers 3` = Run 3 worker processes. Rule of thumb: `(2 × CPU cores) + 1`. For 1 CPU = 3 workers.
- `--bind unix:...gunicorn.sock` = Communicate via a Unix socket (faster than TCP for local communication).
- `estateweb.wsgi:application` = The entry point to your Django app.

**Enable and start the service:**

```bash
sudo systemctl daemon-reload       # Reload systemd to see the new service file
sudo systemctl start gunicorn      # Start Gunicorn
sudo systemctl enable gunicorn     # Auto-start on reboot
sudo systemctl status gunicorn     # Check it's running
```

You should see `Active: active (running)` in green.

**Check logs if something's wrong:**
```bash
sudo journalctl -u gunicorn -n 50
```

---

## Step 10 — Set Up Nginx as a Reverse Proxy

**WHY Nginx?**
Gunicorn is great at running Python code, but it's not optimized for:
- Serving static files (images, CSS, JS)
- Handling HTTPS/SSL
- Handling many simultaneous connections

Nginx is a specialist at all of these. So: **users talk to Nginx, Nginx talks to Gunicorn**.

### Install Nginx

```bash
sudo apt install nginx -y
```

### Create an Nginx Config for Estate Web

```bash
sudo nano /etc/nginx/sites-available/estateweb
```

Paste this:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;  # Max file upload size

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/estateweb/staticfiles;
    }

    location /media/ {
        root /var/www/estateweb;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/estateweb/gunicorn.sock;
    }
}
```

**What each block does:**
- `listen 80` = Accept traffic on port 80 (regular HTTP).
- `server_name` = Only respond to requests for your domain.
- `location /static/` = Serve static files directly — Nginx is fast at this, no need to involve Gunicorn.
- `location /media/` = Serve uploaded files (property images, etc.) directly.
- `location /` = Everything else goes to Gunicorn via the socket file.

### Enable the Site

```bash
# Create a symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/estateweb /etc/nginx/sites-enabled/

# Remove the default Nginx welcome page
sudo rm /etc/nginx/sites-enabled/default

# Test the config for syntax errors
sudo nginx -t
```

You should see:
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Step 11 — Configure Your Domain

**WHY do this?**
Right now your server has an IP address like `65.21.150.44`. Users can't remember IPs — they need a domain like `estateweb.ng`.

### Steps on Namecheap (or wherever you bought the domain):

1. Log into Namecheap → Go to your domain → **Advanced DNS**
2. Delete any existing A records
3. Add these records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | YOUR_SERVER_IP | Automatic |
| A Record | www | YOUR_SERVER_IP | Automatic |

**WHY two records?** `@` covers `yourdomain.com` and `www` covers `www.yourdomain.com`.

**How long does it take?** DNS changes take 15 minutes to 48 hours to propagate globally. Usually under 30 minutes.

**Test if it's working:**
```bash
ping yourdomain.com
```

If it shows your server's IP, it's working.

---

## Step 12 — Install SSL Certificate (HTTPS with Certbot)

**WHY HTTPS?**
Without HTTPS, all data (passwords, form submissions) travels the internet in plain text — anyone on the same network can read it. HTTPS encrypts everything. Also, browsers now show a "Not Secure" warning for HTTP sites, which kills user trust.

Let's Encrypt gives you a FREE, trusted SSL certificate that auto-renews.

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get Your Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will:
1. Verify you own the domain (by placing a file on your server and checking it via HTTP)
2. Generate the certificate
3. Automatically update your Nginx config to use HTTPS
4. Set up auto-renewal

When asked about HTTP redirect: choose **Option 2 (Redirect)** — this forces all HTTP traffic to HTTPS automatically.

### Verify Auto-Renewal

```bash
sudo certbot renew --dry-run
```

If it says "Congratulations, all renewals succeeded" — you're good. Certbot will automatically renew every 90 days.

---

## Step 13 — Set Up Email (Brevo SMTP)

**WHY Brevo (formerly Sendinblue)?**
- Free tier: 300 emails/day — enough for Estate Web early stage
- Reliable delivery (emails won't go to spam as often as direct SMTP)
- Easy setup

### Set Up Brevo

1. Go to [brevo.com](https://www.brevo.com) and create a free account
2. Go to **SMTP & API** settings
3. Generate an SMTP key (password)
4. Your credentials will be:
   - **Host:** `smtp-relay.brevo.com`
   - **Port:** `587`
   - **Username:** Your Brevo account email
   - **Password:** The SMTP key you generated

Update your `.env` file with these values (you should have already added them in Step 7).

### Test Email in Django Shell

```bash
cd /var/www/estateweb
source venv/bin/activate
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    'Test Email from Estate Web',
    'This is a test message.',
    'noreply@yourdomain.com',
    ['youremail@gmail.com'],
    fail_silently=False,
)
```

If no error is raised, your email is working.

---

## Step 14 — Security Best Practices

### A — Django Security Settings

Add these to `settings.py` (only active when `DEBUG=False`):

```python
# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True          # Force HTTPS
SESSION_COOKIE_SECURE = True        # Send cookies only over HTTPS
CSRF_COOKIE_SECURE = True           # Same for CSRF token cookie
SECURE_HSTS_SECONDS = 3600          # Tell browsers to always use HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

**What these do in plain English:**
- `XSS_FILTER` = Tells browsers to block cross-site scripting attacks.
- `SSL_REDIRECT` = Anyone visiting via HTTP gets automatically sent to HTTPS.
- `SESSION_COOKIE_SECURE` = Your login cookies can't be stolen over HTTP.
- `HSTS` = Tells browsers "this site is HTTPS only for the next 3600 seconds."

### B — Keep Software Updated

```bash
# Run this monthly (or set up automatic updates)
sudo apt update && sudo apt upgrade -y
```

### C — Set Up Fail2Ban (Block Brute Force Attacks)

**WHY:** Hackers run automated scripts that try thousands of passwords on SSH. Fail2Ban automatically bans IPs that fail too many times.

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

Default config is fine for now — it will ban IPs after 5 failed SSH attempts for 10 minutes.

---

## Step 15 — How to Restart Services and Debug Common Errors

### Quick Reference — Service Commands

```bash
# Gunicorn
sudo systemctl status gunicorn      # Check if running
sudo systemctl restart gunicorn     # Restart
sudo systemctl stop gunicorn        # Stop
sudo journalctl -u gunicorn -n 100  # View last 100 log lines

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t                       # Test config for errors
sudo tail -f /var/log/nginx/error.log   # Watch errors live

# PostgreSQL
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

### Common Error: 502 Bad Gateway

**Meaning:** Nginx is running but Gunicorn is not (or the socket file is missing/wrong path).

**Fix:**
```bash
sudo systemctl restart gunicorn
sudo journalctl -u gunicorn -n 50   # Check what's wrong
```

### Common Error: Static Files Not Loading (404)

**Meaning:** CSS/JS not found. Usually `collectstatic` wasn't run.

**Fix:**
```bash
cd /var/www/estateweb
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Common Error: 500 Internal Server Error

**Meaning:** Django crashed. Could be a code error, missing env variable, or migration issue.

**Fix:**
```bash
sudo journalctl -u gunicorn -n 100   # Read the actual Python traceback here
```

### Common Error: Permission Denied on Socket

**Fix:**
```bash
sudo usermod -aG www-data estateadmin
sudo chown -R estateadmin:www-data /var/www/estateweb
sudo chmod -R 775 /var/www/estateweb
sudo systemctl restart gunicorn nginx
```

---

## Step 16 — How to Update Your App (Deploy New Code)

Every time you push new code to GitHub and want it live on the server, follow this process:

```bash
# 1. SSH into your server
ssh estateadmin@YOUR_SERVER_IP

# 2. Navigate to your project
cd /var/www/estateweb

# 3. Activate virtual environment
source venv/bin/activate

# 4. Pull latest code from GitHub
git pull origin main

# 5. Install any new dependencies (if requirements.txt changed)
pip install -r requirements.txt

# 6. Run any new migrations
python manage.py migrate

# 7. Collect static files (if CSS/JS changed)
python manage.py collectstatic --noinput

# 8. Restart Gunicorn to load the new code
sudo systemctl restart gunicorn
```

### Pro Tip: Create a Deploy Script

Create a file called `deploy.sh`:

```bash
nano /var/www/estateweb/deploy.sh
```

Paste:
```bash
#!/bin/bash
echo "=== Pulling latest code ==="
git pull origin main

echo "=== Installing dependencies ==="
source /var/www/estateweb/venv/bin/activate
pip install -r requirements.txt

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Restarting Gunicorn ==="
sudo systemctl restart gunicorn

echo "=== Deployment complete! ==="
```

Make it executable:
```bash
chmod +x /var/www/estateweb/deploy.sh
```

Now deploying is just:
```bash
cd /var/www/estateweb && ./deploy.sh
```

---

## Final Checklist

Before going live, confirm all of these:

- [ ] Server is on Ubuntu 22.04
- [ ] Non-root user created (`estateadmin`)
- [ ] UFW firewall enabled (OpenSSH, Nginx Full)
- [ ] Root login disabled
- [ ] Python virtual environment set up
- [ ] PostgreSQL installed, database and user created
- [ ] Django connected to PostgreSQL via `.env`
- [ ] Gunicorn running as a systemd service
- [ ] Nginx configured and pointing to Gunicorn socket
- [ ] Domain A records pointing to server IP
- [ ] SSL certificate installed via Certbot
- [ ] HTTPS redirect working
- [ ] Email tested via Django shell
- [ ] Security settings in `settings.py` confirmed
- [ ] Fail2Ban installed
- [ ] `collectstatic` run successfully
- [ ] `createsuperuser` done

---

## Summary — The Full Stack

```
Internet
   │
   ▼  Port 443 (HTTPS)
[Certbot SSL] ──encrypts──▶ [Nginx]
                                │
                                │ via Unix socket
                                ▼
                          [Gunicorn] (3 workers)
                                │
                                ▼
                          [Django App]
                                │
                                ▼
                         [PostgreSQL DB]
```

Congrats — you've built a production-grade Django deployment from scratch.
This is the same architecture used by real SaaS companies.

---

*Guide prepared for Estate Web — Nigeria's intelligent real estate platform.*
*Keep this document safe. You'll refer to it many times.*