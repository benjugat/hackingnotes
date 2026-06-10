# Hacking Notes

Notes for an ethical hacker — cheatsheets, methodology and references
across web, mobile, network, Active Directory, post-exploitation and more.

The site is built with [MkDocs](https://www.mkdocs.org/) using
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and is
deployed automatically to GitHub Pages on every push to `main`.

> 🌐 Live site: <https://benjugat.github.io/hackingnotes/>

## Stack

- **Static site generator:** MkDocs 1.6
- **Theme:** Material for MkDocs 9.6
- **Markdown extensions:** PyMdown Extensions (superfences, highlight,
  tabbed, details, snippets, tasklist, …)
- **Deploy:** GitHub Actions → `actions/deploy-pages@v4`

## Project layout

```
.
├── docs/                 # Markdown content (one folder per topic)
│   ├── index.md
│   ├── changelog.md
│   ├── active-directory/
│   ├── client-side-attacks/
│   ├── enumeration/
│   ├── exploiting/
│   ├── hacking-wifi/
│   ├── movil/
│   ├── other/
│   ├── post-exploitation/
│   ├── privilege-escalation/
│   ├── reconnaissance/
│   ├── services/
│   ├── software/
│   ├── web/
│   ├── images/           # All images live here
│   └── css/extra.css     # Site-wide custom CSS
├── mkdocs.yml            # Site config & navigation
├── requirements.txt      # Python dependencies
├── .github/workflows/
│   └── deploy.yml        # Build & publish to GitHub Pages
├── migrate_content.py    # One-shot Jekyll → MkDocs migration script
└── MIGRATION_TO_MKDOCS.md
```

## Editing notes

1. Create or edit a Markdown file inside `docs/<topic>/`.
2. Add (or update) the front matter — only `title:` is required:

   ```markdown
   ---
   title: My New Page
   ---

   # Heading
   ...
   ```

3. Reference other pages with a relative `.md` link. MkDocs resolves the
   URL at build time:

   ```markdown
   See [SQLi](../web/sqli.md) for details.
   ```

4. Reference an image with a relative path inside `docs/images/`:

   ```markdown
   ![Alt text](../images/my-image.png)
   ```

5. Open a pull request. The action will preview-build the site and
   publish to GitHub Pages on merge to `main`.

## Local development

You need **Python 3.10+** installed.

```bash
# 1. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the live-reloading dev server
mkdocs serve                     # browse to http://127.0.0.1:8000
```

While the dev server is running, every save to a Markdown file or to
`mkdocs.yml` triggers an automatic rebuild and browser refresh.

## Building the site locally

```bash
mkdocs build --clean
# Output is written to ./site/
```

Use `--strict` to fail the build on any warning (broken internal link,
missing nav entry, …). The CI workflow runs with `--strict` enabled.

## Deploying to GitHub Pages

Deployment is fully automatic:

- Push to `main` (or trigger the workflow manually from the Actions tab).
- The workflow at `.github/workflows/deploy.yml` installs Python 3.11,
  installs dependencies from `requirements.txt`, runs `mkdocs build
  --strict`, and publishes the `site/` directory via the official
  `actions/deploy-pages@v4` action.
- No `gh-pages` branch is used; the site is published straight from the
  workflow artifact.

### One-time GitHub setup

1. Open **Settings → Pages** for the repository.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Save. The next successful workflow run will publish the site.

## Adding a new page to the navigation

New pages are not auto-added to the navigation. Edit `mkdocs.yml` and
append the page to the appropriate section:

```yaml
nav:
  - Web:
      - web/sqli.md
      - web/my-new-page.md   # ← new entry
```

Then run `mkdocs serve` to preview.

## Conventions

- **Filenames** are lowercase, dash-separated (`sql-injection.md`,
  not `SQL_Injection.md`).
- **Folder names** match the section name in `mkdocs.yml`.
- **Front matter**: only `title:` is used. The `category` and `order`
  fields from the old Jekyll site are no longer needed.
- **Images** go into `docs/images/`. Prefer descriptive kebab-case
  filenames (`request-splitting.png` rather than `IMG_1234.png`).

## License

See [`LICENSE`](./LICENSE).
