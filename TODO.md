# Fix Missing hero_bg.jpg Staticfiles Error ✅

**Status: Local Fix Complete**

## Steps:
- ✅ 1. Create TODO.md
- ✅ 2. Edit `core/templates/core/landing.html` → Replaced `{% static "estate/images/hero_bg.jpg" %}` with pure CSS gradient fallback
- [ ] 3. Test locally: `python manage.py runserver`, visit landing page, confirm no console errors and hero looks good
- [ ] 4. In production: `cd /home/deploy/estateweb && python manage.py collectstatic --noinput`
- [ ] 5. Verify prod landing page loads without traceback
- [ ] 6. Mark complete and cleanup TODO.md

**Next:** Run `python manage.py runserver` locally and check `/` (landing page). Hero section should render with smooth dark gradient (no image errors). Confirm in browser dev tools (F12 → no 404s for hero_bg.jpg).

**Production:** After local test, deploy changes to `/home/deploy/estateweb` and run collectstatic.
