# Newsletter

Email subscribers when a new post is published. Subscribers sign up via a form on the blog; a GitHub Actions cron job checks the Atom feed every 4 hours and sends new posts via [Resend](https://resend.com).

## Files

```
_includes/subscribe-form.html      # signup form (include in any layout)
_layouts/base.html                  # overrides minima to show form on every page
netlify/functions/subscribe.py      # Netlify Function: adds contact + sends confirmation
netlify/functions/unsubscribe.py    # Netlify Function: marks contact unsubscribed
newsletter/newsletter.py           # checks feed, emails subscribers
.github/workflows/newsletter.yml   # cron schedule (every 4h) + workflow_dispatch
.sent_posts.json                    # tracks which posts have been emailed (committed to repo)
netlify.toml                        # [functions] directory config (add to existing file)
```

## Setup

### 1. Resend
- Create account, verify your domain, create an Audience
- Note the API key and Audience ID

### 2. GitHub Secrets (Settings → Secrets → Actions)
| Secret | Example |
|--------|---------|
| `RESEND_API_KEY` | `re_...` |
| `RESEND_AUDIENCE_ID` | `aud_...` |
| `BLOG_URL` | `https://yourblog.com` |
| `FROM_EMAIL` | `You <you@yourdomain.com>` |
| `ADMIN_EMAIL` | `you@yourdomain.com` |

### 3. Netlify Environment Variables (Site settings → Environment variables)
`RESEND_API_KEY`, `RESEND_AUDIENCE_ID`, `FROM_EMAIL`

### 4. netlify.toml
Add to your existing `netlify.toml`:
```toml
[functions]
  directory = "netlify/functions"
```

### 5. Seed state
`.sent_posts.json` must list every existing post's feed `<id>` before the first run, or the entire back-catalog gets emailed. The committed file already covers current posts; add any new ones published before merging.

### 6. Subscribe form
Already included on every page via `_layouts/base.html`. To move it, use `{% include subscribe-form.html %}` in any layout or page.
