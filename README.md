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

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. In Streamlit Cloud, set **Secrets** (Manage app → Settings → Secrets):

```toml
APP_ACCESS_PASSWORD = "change-me"
GROQ_API_KEY = "gsk_your_key_here"

[branding]
app_name = "Fluency"
tagline = "Capture expertise in a snap"
page_title = "Fluency"
page_icon = "🗣️"
hide_powered_by = true
```

3. Reboot the app after changes.

## Notes

- Never commit real secrets. This repo gitignores `.streamlit/secrets.toml` and `.streamlit/secrets.local.toml`.
- SOP output is enforced as strict Markdown with the required headers:
  `## Title`, `## Purpose`, `## Roles`, `## Procedures`.

