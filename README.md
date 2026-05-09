# Fluency (Streamlit)

Capture expertise in a snap.

## Run locally

1. Create a virtualenv and install deps:

```bash
pip install -r requirements.txt
```

2. Create secrets file (not committed):

- Preferred: `.streamlit/secrets.toml`
- Fallback (supported by this app): `.streamlit/secrets.local.toml`

Example:

```toml
APP_ACCESS_PASSWORD = "change-me"
GROQ_API_KEY = "gsk_your_key_here"
```

### Self-service signup (SaaS)

By default, the login screen has **Create workspace**: visitors can register a new organization (tenant) and become admin. Omit the key to leave signup **enabled**. Set explicitly to disable:

```toml
SELF_SIGNUP_ENABLED = false
```

### Email verification (magic link, no SMTP)

Open signup is easy to abuse with fake tenants. By default, **new workspace admins must verify email** before they can sign in: after **Create workspace**, they open a **magic link** once (same tab as the app). No in-app SMTP — users copy the link from the success screen or send it to themselves.

Configure in secrets:

```toml
# Canonical app URL for clickable links (Streamlit Cloud: https://your-app.streamlit.app)
APP_BASE_URL = "https://your-app.streamlit.app"

# Default true when unset — set false only for trusted / internal deployments
REQUIRE_EMAIL_VERIFICATION = true

# How long each verification token stays valid (hours)
VERIFICATION_LINK_EXPIRY_HOURS = 48
```

`PUBLIC_URL` is accepted as an alias for `APP_BASE_URL`. If `APP_BASE_URL` is missing, the app still shows the raw `?verify_token=…` fragment and **Sign in → Verify with token (manual)** accepts the token or a pasted full URL.

To turn off verification entirely (not recommended on the public internet):

```toml
REQUIRE_EMAIL_VERIFICATION = false
```

### SaaS mode (recommended)

For client deployments, use a real database and login instead of a shared password.

Add to secrets:

```toml
DATABASE_URL = "postgresql+psycopg2://user:pass@host:5432/fluency"

BOOTSTRAP_TENANT_SLUG = "acme"
BOOTSTRAP_TENANT_NAME = "Acme Inc"
BOOTSTRAP_ADMIN_EMAIL = "admin@acme.com"
BOOTSTRAP_ADMIN_PASSWORD = "change-me"
```

### Quotas / rate limiting

Default quotas (applied when a tenant is created) can be configured via secrets/env:

```toml
DEFAULT_GENERATIONS_PER_DAY = 50
DEFAULT_TRANSCRIPTIONS_PER_DAY = 50
DEFAULT_VISION_PER_DAY = 50
```

3. Start the app:

```bash
streamlit run app.py
```

## PostgreSQL (production / Streamlit Cloud)

Streamlit Community Cloud does **not** give you a durable local disk. Use **PostgreSQL** for tenants, users, SOPs, manuals, and quotas.

**Where is my data?** Your organization’s records (accounts, SOPs, manuals, quotas) live only in **your** PostgreSQL database—the server in `DATABASE_URL` (often [Neon](https://neon.tech)); the Streamlit host runs the app code and **does not** hold a second copy of your data.

1. **Create a Postgres database** (any host works; common choices: [Neon](https://neon.tech), [Supabase](https://supabase.com), [Railway](https://railway.app), [Render](https://render.com), AWS RDS).
2. **Create a database** (e.g. `fluency`) and a user with a strong password.
3. **Connection string for this app** — SQLAlchemy + `psycopg2-binary`:

   ```
   postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE
   ```

   - If the password contains `@`, `#`, `/`, or spaces, **URL-encode** it (e.g. `@` → `%40`).
   - Many cloud providers require TLS. Append query params as your host documents, for example:

   ```
   postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
   ```

4. Put the full string in **`DATABASE_URL`** (local `secrets.toml` or Streamlit Cloud **Secrets**).
5. **First deploy**: the app runs `create_all` on startup; tables are created automatically. No separate migration runner is required for the current schema.
6. **Backups** are your responsibility and are configured in the **database provider’s console**—this app does not run backups for you.

### Backups on Neon (PITR and exports)

If you use **[Neon](https://neon.tech)**:

- Enable **point-in-time restore (PITR)** and a **restore window** that matches your goals ([Backup & restore](https://neon.tech/docs/guides/backup-restore), [Backups](https://neon.tech/docs/manage/backups)—confirm limits for your Neon plan in the dashboard).
- Add **scheduled logical backups** if you need periodic files (e.g. nightly `pg_dump`-style exports or Neon’s backup/export options) for compliance or off-site copies.

Review Neon’s current backup and restore documentation when you go live; tune retention and export cadence to your RPO/RTO.

**Local dev without Postgres:** omit `DATABASE_URL` and the app uses SQLite (`fluency.db`). Do not rely on SQLite for Cloud.

---

## Production secrets checklist

Use this before going live (Streamlit Cloud: **App settings → Secrets**; local: `.streamlit/secrets.toml`).

| Secret / setting | Required? | Notes |
|------------------|------------|--------|
| `GROQ_API_KEY` | **Yes** | LLM + optional STT/vision via Groq. |
| `DATABASE_URL` | **Yes** (prod) | PostgreSQL URL as above. Omit only for local SQLite. |
| `BOOTSTRAP_*` or first admin | **Yes** (recommended) | Set `BOOTSTRAP_ADMIN_EMAIL` + `BOOTSTRAP_ADMIN_PASSWORD` (and optionally tenant slug/name). On each app load, if that email **does not** exist in the DB yet, the app creates an admin user on Postgres (Neon). Alternate secret names: `bootstrap_admin_email`, `database_url`, etc. Or use the in-app “Create first admin” form when there are zero users and no bootstrap secrets. |
| `AUTH_DISABLED` | No | Leave **unset** or `false` in production. |
| `SELF_SIGNUP_ENABLED` | No | Default **on**: “Create workspace” public signup. Set `false` for invite-only tenants. |
| `DEBUG_ERRORS` | No | Leave **unset** or `false` in production; use `true` only while debugging. |
| `APP_ACCESS_PASSWORD` | No | Optional extra gate **before** login; SaaS usually uses login only. |
| `SESSION_COOKIE_SECRET` | **Recommended** (prod) | Long random string (e.g. `openssl rand -hex 32`). Enables a signed browser cookie so **a full page refresh** keeps the user signed in (Streamlit’s server session alone does not). Without this secret, users return to the login screen after refresh. |
| `SESSION_COOKIE_DAYS` | No | Sign-in cookie lifetime in days (default **30**, max **366**). |
| `APP_LOG_PATH` | No | Overrides log file path (default uses system temp). |
| `DEFAULT_*_PER_DAY` | No | Quota defaults for new tenants (`DEFAULT_GENERATIONS_PER_DAY`, etc.). |
| `[branding]` | No | Optional white-label (see `.streamlit/secrets.toml.example`). |

After changing secrets on Streamlit Cloud, **restart the app** (Redeploy / reboot).

---

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Provision **PostgreSQL** and copy the JDBC-style URL into `DATABASE_URL` (see above).
3. In Streamlit Cloud, set **Secrets** (Manage app → Settings → Secrets). Minimal production example:

```toml
GROQ_API_KEY = "gsk_your_key_here"
DATABASE_URL = "postgresql+psycopg2://user:pass@host:5432/fluency?sslmode=require"

BOOTSTRAP_TENANT_SLUG = "acme"
BOOTSTRAP_TENANT_NAME = "Acme Inc"
BOOTSTRAP_ADMIN_EMAIL = "admin@example.com"
BOOTSTRAP_ADMIN_PASSWORD = "use-a-strong-password"

# Optional branding
# [branding]
# app_name = "Fluency"
# tagline = "Capture expertise in a snap"
# page_title = "Fluency"
# page_icon = "🗣️"
# hide_powered_by = true
```

4. Reboot the app after changes.

## Redeploy + smoke test (Streamlit Cloud + Neon)

After you push the latest code (including the self-signup default fix):

1. **Streamlit Cloud** → your app → **Reboot** (or trigger a new deploy from Git).
2. In **Secrets**, confirm **`DATABASE_URL`** is your Neon Postgres URL (not empty). Optional: add `SHOW_DB_HINT = true` temporarily — the login page will show **Deployment DB: PostgreSQL** (remove after testing).
3. Open the app URL. You should see **Sign in** and **Create workspace** (unless `SELF_SIGNUP_ENABLED = false`).
4. **Create workspace**: use a new workspace URL, org name, email, password (8+ chars). Submit → you should see a **verification link** (with **`APP_BASE_URL`** set in Secrets) or a `?verify_token=…` line. Open the link **or** use **Sign in → Verify with token** once; then **Sign in** with the same email and password. Until verified, sign-in shows “Email not verified”.
5. After login, open the sidebar **Usage & quotas** expander — it shows **Database: PostgreSQL** when `DATABASE_URL` is set. If it says **SQLite (dev only)**, Cloud is not using Neon (check secrets and reboot).
6. In **Neon** (dashboard / query), confirm new rows in your tables (e.g. `tenants`, `users`) after signup.
7. Set **`SHOW_DB_HINT = false`** or remove it, and keep **`DEBUG_ERRORS`** off in production.

## Troubleshooting login (“Invalid email or password”)

- **Wrong database (common):** The app caches one SQLAlchemy engine **per `DATABASE_URL`**. After adding or changing Neon `DATABASE_URL`, **redeploy/reboot** the app so new connections use Postgres. Check sidebar **Usage & quotas → Database:** — it must say **PostgreSQL**, not **SQLite (dev only)** on Cloud.
- Use the **same email** you registered with (check spelling; emails are stored lowercase).
- Passwords are **trimmed** when checking; legacy passwords saved without trimming are still accepted when needed.
- Sign-up on **Streamlit Cloud + Neon** is a **different database** than local SQLite: accounts created locally do not exist in Neon until you create them there.
- If your admin was created with **bootstrap secrets**, sign in with **`BOOTSTRAP_ADMIN_EMAIL`** / **`BOOTSTRAP_ADMIN_PASSWORD`** exactly as in Secrets (after trimming).
- Temporary diagnostics: add **`DEBUG_LOGIN = true`** to Streamlit Secrets, retry sign-in, open the **Login debug** expander (then remove the secret).

## Notes

- Never commit real secrets. This repo gitignores `.streamlit/secrets.toml` and `.streamlit/secrets.local.toml`.
- SOP output is enforced as strict Markdown with the required headers:
  `## Title`, `## Purpose`, `## Roles`, `## Procedures`.

