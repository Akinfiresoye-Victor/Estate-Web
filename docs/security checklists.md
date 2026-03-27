# Estate Web — Pre-Launch Security Checklist

This document covers every security measure you need before going live.
Each item explains **what the threat is**, **why it matters for Estate Web specifically**,
and **exactly what to do**.

---

## 1. Authentication and Account Access

### 1.1 Never expose user IDs in URLs
**Threat:** If your URLs look like `/agent/profile/12/`, an attacker can just change
`12` to `13` and access another user's profile or data.

**What to do:**
- Use UUIDs instead of integer IDs in URLs wherever possible
- You already have `agent_uuid` and `unique_company_id` — use those in URLs, not `pk`

```python
# BAD — exposes database ID
path('agent/edit/<int:pk>/', views.edit_agent)

# GOOD — UUID is unguessable
path('agent/edit/<str:agent_uuid>/', views.edit_agent)
```

---

### 1.2 Always verify ownership before allowing edits or deletes
**Threat:** An agent could craft a URL like `/update-property/999/` and edit
another agent's listing if you only check that they are logged in.

**What to do:** Every view that modifies data must confirm the logged-in user
owns that object.

```python
# BAD — only checks login
@login_required
def update_property(request, property_id):
    prop = PropertyManagementSale.objects.get(pk=property_id)
    # Anyone logged in can edit this

# GOOD — checks ownership
@login_required
def update_property(request, property_id):
    prop = get_object_or_404(
        PropertyManagementSale,
        pk=property_id,
        agent_uuid=request.user.agentinformation.agent_uuid  # must be theirs
    )
```

Apply this to every view that does: update property, delete property,
update profile, view leads, view analytics, manage company.

---

### 1.3 Role checks on every protected view
**Threat:** A customer could navigate directly to `/agent/dashboard/` or
`/company/analytics/` if you forget to check the role.

**What to do:** Every agent/company view must have a role check at the top.
You already do this in most views — audit every single view and confirm
none are missing this check.

```python
if request.user.role != 'agent':
    messages.error(request, 'Agents only')
    return redirect('landing')
```

Views to audit specifically:
- All `agent:` namespace views
- All `company:` namespace views
- `toggle-listing` — agents only, and must own the property
- `delete-property-s` and `delete-property-r` — must own the property
- `update-property` and `update-property-s` — must own the property
- `company:generate_invite_link` — company admin only
- `company:find-talents` — company only
- `agent:update-agent` — agent must match the UUID in the URL

---

### 1.4 Password strength enforcement
**Threat:** Users set weak passwords like `12345` and get brute-forced.

**What to do:** Django has built-in validators — make sure these are all
active in `settings.py`:

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

---

### 1.5 Rate limit login attempts
**Threat:** Attackers run scripts that try thousands of password combinations
(brute force). Without rate limiting, nothing stops them.

**What to do:** Install `django-axes`:

```bash
pip install django-axes
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    'axes',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 5        # lock after 5 failed attempts
AXES_COOLOFF_TIME  = 1        # lock for 1 hour
AXES_LOCKOUT_PARAMETERS = ['ip_address', 'username']  # lock by IP and username
```

---

### 1.6 Secure the password reset flow
**Threat:** If password reset tokens do not expire, an attacker who intercepts
an old reset email can use it months later.

Django's default reset tokens expire after 3 days. Tighten this:

```python
# settings.py
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour in seconds (default is 259200 = 3 days)
```

---

### 1.7 Session security
**Threat:** Session hijacking — attacker steals the session cookie and
impersonates the user.

```python
# settings.py
SESSION_COOKIE_HTTPONLY = True   # JS cannot read the cookie
SESSION_COOKIE_SECURE   = True   # cookie only sent over HTTPS (Render uses HTTPS)
SESSION_COOKIE_SAMESITE = 'Lax'  # blocks cross-site request cookie leaks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600     # 2 weeks in seconds
```

---

## 2. CSRF Protection

### 2.1 CSRF on all POST requests
**Threat:** Cross-Site Request Forgery — an attacker tricks a logged-in user
into submitting a form on your site from a malicious external page.

Django's `CsrfViewMiddleware` is on by default. Make sure you have not
accidentally disabled it anywhere.

**Check `settings.py`:**
```python
MIDDLEWARE = [
    ...
    'django.middleware.csrf.CsrfViewMiddleware',  # must be present
    ...
]
```

**Check every HTML form:** Every `<form method="POST">` must have `{% csrf_token %}` inside it.

**Check every AJAX call:** Your project already includes `X-CSRFToken` in AJAX
headers — confirm every fetch call in every JS file follows this pattern:

```javascript
fetch(url, {
    method: 'POST',
    headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': CSRF,
    },
    credentials: 'same-origin',
})
```

Views to check specifically: `toggle-listing`, `toggle-wishlist-buy`,
`toggle-wishlist-rent`, `remove agent from company`, `generate_invite_link`.

---

## 3. Data Exposure and Information Leakage

### 3.1 Never return raw exception messages to users
**Threat:** Stack traces and exception messages expose your database structure,
file paths, model names, and logic to attackers.

You already have `error_page.html` but check what you pass to it:

```python
# BAD — exposes internal error details to the user
return render(request, 'estate/error_page.html', {'e': e})

# GOOD — log the real error server-side, show a generic message to the user
import logging
logger = logging.getLogger(__name__)

logger.error(f"Error in company_analytics: {e}", exc_info=True)
return render(request, 'estate/error_page.html', {'e': 'Something went wrong. Please try again.'})
```

Set `DEBUG = False` in production — this is critical. With `DEBUG = True`,
Django shows a full stack trace to anyone who triggers an error.

```python
# settings.py (production)
DEBUG = False
ALLOWED_HOSTS = ['estatewebng.com', 'www.estatewebng.com']
```

---

### 3.2 Do not expose agent UUIDs or company UUIDs in template source unnecessarily
**Threat:** Developers sometimes pass full model objects to templates and the
template renders sensitive fields in HTML comments or hidden inputs without
realising.

**What to do:** Audit your templates — search for `{{ agent_info }}`,
`{{ company }}` renders. Make sure UUIDs, government ID fields, BVN-adjacent
data, and internal IDs are not rendered in the HTML unless they are actually
needed on that page.

---

### 3.3 Protect media files — government IDs and certificates
**Threat:** Files uploaded to `/media/` are publicly accessible by URL if
Django is serving them directly. An attacker who guesses or finds the URL
for a government ID image can download it directly.

**What to do:**

For sensitive documents (`government_id`, `certificate`, any KYC files),
serve them through a view that checks authentication and ownership:

```python
@login_required
def serve_private_document(request, filename):
    # Only the agent themselves or a staff user can access
    agent = get_object_or_404(AgentInformation, user=request.user)
    if not agent.government_id or filename not in agent.government_id.name:
        raise PermissionDenied
    # Serve the file using X-Accel-Redirect (Nginx) or FileResponse
    from django.http import FileResponse
    return FileResponse(open(agent.government_id.path, 'rb'))
```

Property images and profile pictures can remain public — they are
intentionally public-facing. Only KYC documents need this protection.

---

### 3.4 Do not leak user emails in public pages
**Threat:** Agent and company profiles display contact information. If you
render the raw email in the HTML, scrapers harvest it for spam.

**What to do:** On public profiles, consider showing a contact form instead
of the raw email, or obfuscate it. The phone number used for WhatsApp is
fine to display since that is the intended contact method for Nigerian users.

---

## 4. SQL Injection and Input Validation

### 4.1 Always use Django ORM — never raw SQL with user input
**Threat:** If you ever use `cursor.execute()` with user-provided values
concatenated as strings, attackers can manipulate your database queries.

Django's ORM parameterises all queries automatically so you are protected
as long as you use it correctly.

```python
# BAD — never do this
cursor.execute(f"SELECT * FROM leads WHERE name = '{user_input}'")

# GOOD — ORM handles parameterisation
LeadInfo.objects.filter(name=user_input)

# ALSO GOOD — if you must use raw SQL, use parameterised queries
cursor.execute("SELECT * FROM leads WHERE name = %s", [user_input])
```

Search every file for `cursor.execute` and `raw(` and audit each one.

---

### 4.2 Validate all user-supplied data in forms
**Threat:** Users submit unexpected values — negative prices, text where a
number is expected, or manipulated choices that bypass your dropdown options.

**What to do:** Use Django forms or DRF serializers for all input. Never
trust `request.POST` values directly without validation.

```python
# BAD
price = request.POST['price']
PropertyManagementSale.objects.create(price=price, ...)

# GOOD
form = SellPropertyForm(request.POST)
if form.is_valid():
    form.save()
```

---

## 5. Cross-Site Scripting (XSS)

### 5.1 Django auto-escapes template output — do not disable it
**Threat:** If a user submits `<script>alert('hacked')</script>` as a
property description and you render it unescaped, it executes in every
visitor's browser.

Django escapes template variables by default. The danger is when you
use `{{ value|safe }}` or `{% autoescape off %}` — these bypass protection.

**What to do:** Search your templates for `|safe` and `autoescape off`.
Each one is a potential XSS hole. Only use `|safe` when you are absolutely
certain the content is trusted (e.g. your own hardcoded HTML, never
user input).

---

### 5.2 Sanitise rich text fields
**Threat:** If you allow formatted text in property descriptions and render
it as HTML, users can inject scripts.

**What to do:** If you ever add a rich text editor (like TinyMCE or Quill),
install `bleach` to sanitise the output:

```bash
pip install bleach
```

```python
import bleach

ALLOWED_TAGS = ['b', 'i', 'u', 'p', 'br', 'ul', 'ol', 'li']
clean_description = bleach.clean(user_html, tags=ALLOWED_TAGS, strip=True)
```

---

## 6. File Upload Security

### 6.1 Validate file types on upload
**Threat:** An attacker uploads a `.py`, `.php`, or `.exe` file disguised
as a property image. If your server executes it, full system compromise.

**What to do:** Validate both the extension and the actual file content
(MIME type) — not just the filename, which can be faked.

```python
import magic  # pip install python-magic

def validate_image(file):
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    file_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # reset after reading
    if file_type not in allowed_types:
        raise ValidationError('Only JPEG, PNG, and WebP images are allowed.')
```

Add this validator to every `ImageField` and `FileField` in your models.

---

### 6.2 Limit file upload size
**Threat:** An attacker uploads a 2GB file and crashes your server or fills
your storage.

```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880   # 5MB max for form data
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880   # 5MB max for file uploads
```

Also enforce this at the form/model level with a validator:

```python
def validate_file_size(file):
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError('File size must be under 5MB.')
```

---

### 6.3 Store uploads outside the web root on production
**Threat:** Files stored in a public directory can be accessed directly by URL.

On Render, you are using a cloud storage service or the filesystem.
Make sure sensitive uploads (government IDs, certificates) are stored
in a private bucket/directory and served through authenticated views
as described in section 3.3.

For property images and profile pictures (which are public), this is fine.

---

## 7. Invite Link Security

### 7.1 Expire invite links
**Threat:** A company generates an invite link in 2025. In 2027, someone
finds the link and joins the company without permission.

Your handoff notes already flag this as pending. Before launch:

```python
# CompanyInformation model — add this field
invite_link_expiry = models.DateTimeField(null=True, blank=True)

# In generate_invite_link view
company.invite_link_expiry = timezone.now() + timedelta(days=7)
company.save()

# In the view that processes the invite link
if company.invite_link_expiry < timezone.now():
    messages.error(request, 'This invite link has expired.')
    return redirect('landing')
```

---

### 7.2 Invalidate the invite link after use (optional but recommended)
**Threat:** A shared invite link can be used by anyone who sees it — not
just the intended person.

Consider regenerating `unique_company_id` used for invites after each
successful join, or use a separate one-time token field.

---

## 8. API and AJAX Endpoint Security

### 8.1 Return 401 for unauthenticated AJAX requests, not a redirect
**Threat:** Your AJAX views currently redirect to login for unauthenticated
requests. The JS code checks for a 401 status to redirect. If the view
redirects instead of returning 401, the JS gets a 200 with login page HTML
and breaks silently.

**What to do:** In all AJAX-only views, return 401 explicitly:

```python
def toggle_wishlist(request, property_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
```

Your JS already handles this correctly — just make sure the views
return the right status code.

---

### 8.2 Confirm AJAX views only accept POST
**Threat:** A GET request to a state-changing endpoint (like toggle-listing
or toggle-wishlist) can be triggered by simply embedding the URL in an
`<img src="">` tag on another website, bypassing CSRF.

```python
from django.views.decorators.http import require_POST

@require_POST
def toggle_listing(request, property_type, property_id):
    ...
```

Apply `@require_POST` to every view that changes data:
`toggle-listing`, `toggle-wishlist-buy`, `toggle-wishlist-rent`,
`remove agent from company`, `generate_invite_link`.

---

## 9. Django Settings for Production

### 9.1 Full production settings checklist

```python
# settings.py — confirm every one of these before deploying

DEBUG = False
SECRET_KEY = config('SECRET_KEY')  # from environment variable, never hardcoded

ALLOWED_HOSTS = ['estatewebng.com', 'www.estatewebng.com']

# HTTPS enforcement
SECURE_SSL_REDIRECT          = True   # redirect all HTTP to HTTPS
SECURE_HSTS_SECONDS          = 31536000  # tell browsers to always use HTTPS for 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD          = True
SECURE_PROXY_SSL_HEADER      = ('HTTP_X_FORWARDED_PROTO', 'https')  # needed on Render

# Cookie security
SESSION_COOKIE_SECURE   = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE      = True
CSRF_COOKIE_HTTPONLY    = True

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'
```

---

### 9.2 Never commit `.env` to Git
**Threat:** If your `.env` file (containing `SECRET_KEY`, database password,
Paystack secret key) is pushed to GitHub, it is publicly readable.

**What to do:**

1. Make sure `.env` is in your `.gitignore`:
```
.env
*.env
```

2. Check your Git history — if `.env` was ever committed, rotate all secrets
immediately (new `SECRET_KEY`, new database password, new API keys).

3. On Render, set all environment variables in the dashboard, not in `.env`.

---

### 9.3 Rotate your SECRET_KEY before launch
**Threat:** If your `SECRET_KEY` was ever exposed (committed to Git, shared
in a chat), all session tokens and CSRF tokens generated with it are
compromised.

Generate a fresh one:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Set it in Render's environment variables and remove it from any local files
before pushing.

---

## 10. Nigeria-Specific Threats

### 10.1 Fake listing injection
**Threat:** Bad actors create agent accounts and post fraudulent property
listings to scam buyers. This is a real and common problem in Nigerian
real estate.

**What to do (already partially in your Terms):**
- The `Verified` badge system is your main defence — make KYC verification
  mandatory before an agent can go live with listings
- Implement a report listing button on every property card
- Consider a manual review queue for new agents' first 3 listings

---

### 10.2 Account enumeration via login errors
**Threat:** If your login page says "No account with this email" vs
"Wrong password", attackers can confirm which emails are registered
and target them.

**What to do:** Use the same generic error message for both cases:

```python
# BAD
if not user:
    messages.error(request, 'No account found with this email')
if not check_password:
    messages.error(request, 'Wrong password')

# GOOD — same message either way
messages.error(request, 'Invalid email or password')
```

---

### 10.3 Phone number enumeration
Same principle as above — if your registration form says "This phone number
is already registered", attackers can check if specific Nigerian numbers
have accounts. Use a generic "Account already exists" message instead.

---

## 11. Dependency Security

### 11.1 Keep packages updated
**Threat:** Old versions of Django, Pillow, and other packages have known
security vulnerabilities that are publicly documented and exploited.

```bash
# Check for known vulnerabilities in your installed packages
pip install pip-audit
pip-audit
```

Run this before launch and again every few months.

---

### 11.2 Pin your dependencies
**Threat:** If your `requirements.txt` does not pin versions, a future
`pip install` might pull in a compromised package version.

```bash
# Generate a pinned requirements file
pip freeze > requirements.txt
```

---

## 12. Quick Pre-Launch Audit Checklist

Go through this list and tick off each item before you go live:

- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is in environment variable, not hardcoded
- [ ] `.env` is in `.gitignore` and never committed
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] Every view that modifies data has `@require_POST`
- [ ] Every edit/delete view checks object ownership, not just login
- [ ] Every agent/company view has a role check
- [ ] Login rate limiting (`django-axes`) is installed and configured
- [ ] File upload validation is on every `ImageField` and `FileField`
- [ ] `DATA_UPLOAD_MAX_MEMORY_SIZE` is set
- [ ] Government ID / certificate files are served through authenticated views
- [ ] No `{{ value|safe }}` on user-generated content in templates
- [ ] AJAX views return `401` for unauthenticated requests
- [ ] Invite links have an expiry date
- [ ] Error pages show generic messages, not raw exceptions
- [ ] `pip-audit` run with no critical vulnerabilities
- [ ] `PASSWORD_RESET_TIMEOUT` tightened to 1 hour
- [ ] `AUTH_PASSWORD_VALIDATORS` all active in settings

---

*Last updated for Estate Web pre-launch — March 2026*