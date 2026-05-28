# contabia-site

ContabIA web presence. One repo, two deploy surfaces.

## Structure

```
apps/
  marketing/    → contabia.co (public marketing site, blog, free scan, signup)
  portal/       → app.contabia.co (logged-in product surface)
shared/
  css/, components/, assets/  (used by both surfaces)
```

## Deployment

Both surfaces deploy via Cloudflare Pages on push to main:
- `contabia-site` Pages project → `apps/marketing/` → contabia.co
- `contabia-app` Pages project → `apps/portal/` → app.contabia.co

## Local preview

Open any `.html` file directly in a browser, or:

```bash
cd apps/marketing && python3 -m http.server 8000   # → http://localhost:8000
cd apps/portal    && python3 -m http.server 8001   # → http://localhost:8001
```

## Password gate

Both surfaces use a sessionStorage password gate ("Scrooge") until public
launch. Find-and-replace removes it across all HTML files when ready.

## Reference docs

See project knowledge files:
- File 15 — Website & Digital Infrastructure (deployment, domain strategy)
- File 18 — Portal Spec & Free Scan Flow (portal architecture)
- File 14 — Brand Identity / Visual Specs (Caribe Profesional palette, type)
