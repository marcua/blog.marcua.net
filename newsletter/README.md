# Newsletter

Email subscribers when a new post is published. Subscribers sign up via a form on the blog; a GitHub Actions cron job checks the Atom feed every 4 hours and sends new posts via SMTP.

Subscriber data lives in an [ayb](https://github.com/marcua/ayb) database. A `sends` table tracks which (post, subscriber) pairs have been emailed, guaranteeing at-most-once delivery per pair.

On cold start (empty `posts` table), the script records all current feed posts without sending, so the back-catalog is never emailed.

## Files

```
newsletter/newsletter.py                # checks feed, emails subscribers via SMTP
newsletter/migrations.py                # schema DDL (subscribers, posts, sends)
netlify/functions/subscribe.py           # Netlify Function: adds subscriber + sends confirmation
netlify/functions/unsubscribe.py         # Netlify Function: marks subscriber unsubscribed
netlify/functions/_ayb_client.py         # ayb HTTP client (query, escaping, migrations)
netlify/functions/_shared.py             # shared SMTP, constants, helpers
_includes/subscribe-form.html           # signup form (include in any layout)
_layouts/base.html                       # overrides minima to show form on every page
.github/workflows/newsletter.yml        # cron schedule (every 4h) + workflow_dispatch
netlify.toml                             # [functions] directory config
```

## Setup

### 1. SMTP
- Verify your domain, note SMTP credentials

### 2. ayb
- Create a database (e.g. `marcua/blog-newsletter`)
- Note the API URL and token
- Migrations run automatically on first newsletter run

### 3. GitHub Secrets (Settings → Secrets → Actions)
| Secret | Example |
|--------|---------|
| `BLOG_URL` | `https://yourblog.com` |
| `BLOG_NAME` | `My Blog` |
| `FROM_EMAIL` | `You <you@yourdomain.com>` |
| `REPLY_TO` | `you@yourdomain.com` |
| `ADMIN_EMAIL` | `you@yourdomain.com` |
| `SMTP_HOST` | `smtp.example.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `postmaster@yourdomain.com` |
| `SMTP_PASSWORD` | `...` |
| `AYB_API_URL` | `https://ayb.host/v1/entity/database` |
| `AYB_TOKEN` | `...` |

### 4. Netlify Environment Variables (Site settings → Environment variables)
`BLOG_URL`, `BLOG_NAME`, `FROM_EMAIL`, `REPLY_TO`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `AYB_API_URL`, `AYB_TOKEN`

### 5. netlify.toml
Add to your existing `netlify.toml`:
```toml
[functions]
  directory = "netlify/functions"
```

### 6. Subscribe form
Already included on every page via `_layouts/base.html`. To move it, use `{% include subscribe-form.html %}` in any layout or page.
