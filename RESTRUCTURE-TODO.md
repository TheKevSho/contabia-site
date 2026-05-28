# Restructure TODO — remaining work before merge

The mechanical restructure (apps/marketing + apps/portal + shared) is complete.
Code audit found NO internal path updates needed:
- Marketing site has no "Iniciar sesión" link yet (pre-launch state)
- Portal hrefs are all relative — work as-is when deployed at app.contabia.co root
- Password gate is consistent across both surfaces ("Scrooge")

## Remaining work (all external to this PR)

### 1. Cloudflare Pages — second project for portal (Track B)
- Existing `contabia-site` Pages project: change build output dir from repo root to `apps/marketing/`
- Create new `contabia-app` Pages project: same repo, build output dir = `apps/portal/`
- Verify both serve on .pages.dev URLs

### 2. Domain transfer (Track C — in progress)
- Wix → Porkbun transfer initiated, 5-day clock
- After completion: change nameservers at Porkbun to Cloudflare
- Then build DNS in Cloudflare per `contabia-co-dns-records.md`

### 3. Future polish (not blocking)
- Add "Iniciar sesión" link to marketing nav pointing to `https://app.contabia.co/login.html` when portal goes live
- Extract shared brand tokens (10 colors) to `shared/css/tokens.css` and reference from both surfaces — requires build step or duplication strategy first
- Add DKIM + DMARC records for email auth (separate from this PR)
- Merge portal redesign WIP from `18-portal-redesign-wip/` (separate feature branch)

## When to merge this PR

Safe to merge anytime after:
- Cloudflare Pages second project is set up and verified on `.pages.dev` URL
- DNS is ready (post-transfer)

OR merge now and verify on `.pages.dev` URLs before DNS flip. The split itself is non-breaking — `apps/marketing/` and `apps/portal/` already exist and can be deployed independently.