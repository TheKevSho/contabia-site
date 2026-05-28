# Restructure TODO — manual review before merging this branch

This branch (`restructure/marketing-portal-split`) performed the mechanical
moves automatically. The items below need human review or decisions.

## 1. Internal paths (high priority)

Both surfaces had paths assuming a single domain. Search-and-replace passes:

### apps/marketing/
- Find: `href="/portal/`  or  `href="portal/`  or  `href="contabia.co/portal/`
- Replace with: `href="https://app.contabia.co/`
- Specifically the "Iniciar sesión" header link on every page.

### apps/portal/
- Find: `href="contabia.co/portal/`  or any absolute path to the old portal location
- Replace with: root-relative (`href="/login.html"` etc.) so it works on the app subdomain.

Run from repo root:
```bash
grep -rn "portal/" apps/marketing/ --include="*.html"
grep -rn "contabia.co/portal" apps/ --include="*.html"
grep -rn "Iniciar sesión" apps/marketing/ --include="*.html"
```

## 2. Shared CSS / brand tokens (medium priority)

Currently:
- `apps/marketing/css/style.css` — marketing styles, includes brand colors
- `apps/portal/css/portal.css` — portal styles, ALSO includes brand colors

Action:
- Extract duplicated brand declarations (Caribe Profesional palette, font
  imports, type scale) into `shared/css/tokens.css`.
- Reference from both stylesheets via `@import` OR by `<link>` in HTML head.
- Decide how `shared/` is delivered to each Pages project (see shared/README.md).

## 3. Cloudflare Pages — second project (Track B in spec)

After this branch merges:
- Update existing `contabia-site` project: build output directory = `apps/marketing`
- Create new `contabia-app` project: same repo, build output = `apps/portal`
- Verify both serve on `.pages.dev` URLs before any DNS change.

## 4. Domain transfer (Track C in spec)

- Document all DNS records at Wix (MX, SPF, DKIM, DMARC, CAA) BEFORE touching anything.
- Get EPP code from Wix.
- Initiate transfer at Cloudflare Registrar (~$10, 5–7 days).
- After transfer, recreate DNS records in Cloudflare DNS panel.
- Point `contabia.co` and `www.contabia.co` at `contabia-site.pages.dev`.
- Point `app.contabia.co` at `contabia-app.pages.dev`.

## 5. Portal redesign WIP (separate workstream)

The redesigned portal pages live in `~/.../18-portal-redesign-wip/`:
- portal-shell.html (new)
- resumen-owner.html (new)
- reconciliacion.html (860 lines, expanded from current 331)
- mockup-brief.md (design decisions doc)

These were NOT included in this restructure — keeping that work separate
since the restructure spec is "purely organizational, no visual changes."
Merge into `apps/portal/` on a separate feature branch once the redesign
is reviewed.

## 6. Acceptance criteria

Per spec Track G — run through the 12 verification steps after Tracks A-D
are complete and DNS has propagated.

## 7. Delete this file

Once the branch is merged and the restructure is verified live, delete
RESTRUCTURE-TODO.md. It's intentionally noisy as a checklist.
