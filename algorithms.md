📋 Card Title: Feature: Smart Team Onboarding (Invite Links)

Description

A high-speed, secure onboarding flow that allows a Company Admin to link 100+ agents to their company_uuid without manual individual approvals. This replaces the slow "Request-to-Join" queue with a "Self-Serve" model.

1. The Admin Experience (The "Push")

Generate Link: Inside the Company Dashboard, the Admin clicks "Generate Invite Link."

Link Configuration:

Expiration: Set the link to expire in 24h, 48h, or 7 days.

Usage Limit: Optional toggle to limit the link to $X$ number of uses (e.g., 100 uses for 100 agents).

The Payload: The system generates a URL containing a hashed signature or a unique invite_token.

Example: estateweb.com/join?token=abc123companyxyz

One-Click Share: A "Copy to Clipboard" button so the Admin can blast it out via WhatsApp, Slack, or Email.

2. The Agent Experience (The "Pull")

Landing Page: When an agent clicks the link, they see a branded "Welcome to Estate Web" page: "You’ve been invited to join [Company Name] on Estate Web."

Auto-Association: * If the agent is New: During registration, the company_uuid is hidden in the form logic and automatically assigned upon account creation.

If the agent is Existing: They log in, and a pop-up asks: "Would you like to link your profile to [Company Name]?"

Instant Access: Upon completion, the Agent’s profile is instantly updated with the company_uuid, giving them immediate access to company listings.

3. Security & Control (The "Safety Net")

The Kill Switch: The Admin can "Revoke" or "Refresh" the link at any time. If a link is leaked publicly, revoking it makes the old URL dead instantly.

The Audit Log: A small table in the Admin Dashboard showing: “Agent [Name] joined via Invite Link at 10:45 AM.”

Offboarding: A "Remove" button next to each agent's name in the company roster. Clicking this nullifies the company_uuid on the Agent's record, instantly booting them from the company's private data.

4. Why this wins for "Estate Web"

Speed: A 100-person company can be fully onboarded in 5 minutes.

Scalability: It works the same for 2 agents or 2,000 agents.

Professionalism: It makes your startup look like a polished, enterprise-ready platform.



## Smart Invite Link — Algorithm Breakdown

Here's the full mental model, broken into phases. Think of it like a pipeline — each phase feeds the next.

---

### Phase 1: The InviteLink Model (What You Need to Store)

Before anything works, you need a table/model to **remember** every invite link ever created. Each row in this table should hold:

- `invite_token` — a randomly generated unique string (this is what goes in the URL)
- `company` — a FK to the `CompanyInformation` that created it
- `created_at` — timestamp of creation
- `expires_at` — calculated from creation time + admin's chosen duration (24h/48h/7d)
- `max_uses` — optional integer cap (e.g. 100). If admin didn't set one, store `null` meaning unlimited
- `use_count` — starts at 0, increments each time an agent successfully uses the link
- `is_active` — boolean, defaults to `True`. The Kill Switch sets this to `False`

> Think of `invite_token` like a **ticket stub** — it carries no sensitive info itself, but the system looks it up in the database to find out everything about it.

---

### Phase 2: Generating the Link (Admin Side)

When the Admin clicks "Generate Invite Link":

1. **Receive** the admin's chosen expiry duration and optional use limit from the form
2. **Calculate** `expires_at` by adding the chosen duration to `now()`
3. **Generate** a cryptographically secure random token — use Python's `secrets` module (NOT `random`). It should be long enough to be unguessable (32+ characters)
    > `secrets` is specifically designed for tokens/passwords. `random` is predictable and breakable — never use it for security stuff
4. **Save** a new `InviteLink` row with all the fields above
5. **Build** the full URL by appending the token to your base URL: `estateweb.com/join?token=<token>`
6. **Return** that URL to the admin's dashboard for copying

---

### Phase 3: Validating the Link (When an Agent Clicks It)

When someone hits `/join?token=abc123`:

1. **Extract** the token from the URL query params
2. **Look up** the `InviteLink` row where `invite_token` matches
3. **Run the 4 Validity Checks** (if ANY fail, reject the link):
   - Does this token even exist in the database? → if not, **Invalid Token**
   - Is `is_active` still `True`? → if not, **Link Revoked**
   - Is `now()` still before `expires_at`? → if not, **Link Expired**
   - If `max_uses` is not null, is `use_count` still less than `max_uses`? → if not, **Link Full**
4. If all checks pass → **store the token in the session** (Django's `request.session`). This is how you'll remember which company this agent is joining across page loads
   > The session is like a temporary sticky note attached to that browser. It survives redirects and page changes within that visit

---

### Phase 4: Connecting to Your Existing `onboard_agent` View

Your existing view already handles the **actual linking** perfectly — it takes `agent_uuid` in the URL and connects the agent to a company. The invite system just needs to **feed it the right `agent_uuid`** and **know which company to use**.

Here's the routing logic depending on who clicked the link:

#### If the agent is NOT logged in (New or returning, unrecognized):
1. Show the branded landing page: "You've been invited to join [Company Name]"
2. Redirect them to **login or register**
3. After they authenticate, check `request.session` for the stored token
4. Retrieve the `company` from the `InviteLink` using that token
5. Now you have both `agent_uuid` (from the logged-in user) and `company` info
6. **Redirect** to your existing `onboard_agent` view: `/onboard/<agent_uuid>/` — but you need the view to know which company to use. Since your view pulls the company from `request.user`, you just need the **company admin's user to not be the one logged in** — so instead of redirecting to that view directly, you call your onboarding logic in a **new invite-completion view** that replicates what `onboard_agent` does but uses the company pulled from the `InviteLink` row rather than `request.user`

#### If the agent IS already logged in:
1. Token is in session, agent is authenticated
2. Show the pop-up: "Would you like to link your profile to [Company Name]?"
3. If they confirm → same invite-completion logic as above

---

### Phase 5: Post-Onboarding Cleanup

After a successful onboarding via invite link:

1. **Increment** `use_count` on the `InviteLink` row by 1
2. **Log it** — create a `CompanyActivityLog` entry (you already do this in your view, just add context like "joined via invite link")
3. **Clear** the invite token from the session so it can't be reused in the same browser session

---

### Phase 6: The Kill Switch (Admin Revokes Link)

Simple:

1. Admin clicks "Revoke" on a specific link in the dashboard
2. Find the `InviteLink` row by token or its primary key
3. Set `is_active = False` and save
4. That link now **fails** **Check 2** in Phase 3 — instantly dead

"Refresh" means: revoke the old one and generate a brand new token (Phase 2 again).

---

### Phase 7: The Audit Table (Dashboard View)

Your `CompanyActivityLog` already exists. You just need to:

1. When logging onboarding events, store extra detail: which token was used, the agent's name, and the timestamp
2. In the admin dashboard, filter logs by `company` and display them in a table

---

### Security Notes on Your Existing View

A couple of things worth flagging in `onboard_agent`:

1. **The `except Exception as e` at the bottom** passes the raw exception `e` to the template — in production this can leak sensitive internal details (model names, file paths, etc.) to users. Consider logging `e` server-side and showing a generic message to the user instead
2. **The `redirect(request, ...)` call** at the bottom of the except block is wrong syntax — `redirect()` doesn't take a `request` as first argument. That line would crash. It should be `render(request, 'estate/error_page.html', {'e': e})` or a plain `redirect('landing')`