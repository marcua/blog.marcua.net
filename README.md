# Publishing cycle

(from https://github.com/jekyll/jekyll-compose)
`jekyll draft "My new draft"`

`jekyll rename _drafts/my-new-draft.md "My Renamed Draft"`

`jekyll publish _drafts/my-new-draft.md --date YYYY-MM-DD`

`jekyll compose "My New Thing" --collection "things"`

# Preview
`timeout 2h jekyll serve --drafts --future --host 0.0.0.0 --port 8000`

