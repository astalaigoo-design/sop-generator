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
6. **Backups** are your responsibility on the Postgres provider (enable PITR / scheduled backups).

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

## Notes

- Never commit real secrets. This repo gitignores `.streamlit/secrets.toml` and `.streamlit/secrets.local.toml`.
- SOP output is enforced as strict Markdown with the required headers:
  `## Title`, `## Purpose`, `## Roles`, `## Procedures`.

