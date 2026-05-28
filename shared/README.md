# shared/

Brand tokens, shared components, and assets used by both `apps/marketing/`
and `apps/portal/`.

## What goes here

- `css/tokens.css` — Caribe Profesional palette as CSS custom properties,
  type scale, spacing scale. Extract from the duplicated brand declarations
  currently in `apps/marketing/css/style.css` and `apps/portal/css/portal.css`.
- `components/logo.svg` — the ContabIA wordmark (IA in Terracotta).
- `components/footer.html` — shared footer HTML snippet.
- `assets/` — images, icons used by both surfaces.

## How surfaces reference shared/

Use root-relative paths from each Pages project. Since Cloudflare Pages
deploys `apps/marketing/` as the root of one site and `apps/portal/` as
the root of another, `shared/` will need to be COPIED into each surface's
build output, OR referenced via a third Pages project / CDN.

**Decision pending:** Easiest path is to symlink or copy `shared/` into
both `apps/marketing/shared/` and `apps/portal/shared/` at build time.
For a no-build static site, this means either:
  (a) Duplicate the files (simple, lose DRY)
  (b) Use a tiny build step (npm script that copies shared/ into each
      apps/ folder before Cloudflare picks up the deploy)
  (c) Move shared assets into Cloudflare R2 / a separate Pages project
      at `static.contabia.co` and reference via absolute URL.

See RESTRUCTURE-TODO.md.
