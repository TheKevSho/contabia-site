# ContabIA Portal Chat Gateway

Railway-deployed Hermes gateway that lets the ContabIA portal (`app.contabia.co`)
chat with Tayrona's Hermes agent over an OpenAI-compatible API, replacing the
old local `127.0.0.1:8642` server.

> **Status:** ✅ Live — gateway healthy, end-to-end path verified (2026-08-30).

---

## Architecture

```
app.contabia.co (portal UI, Cloudflare Pages, gated by Cloudflare Access)
        │  POST /entities/{id}/chat  (bearer = portal login token)
        ▼
api.contabia.co  ──  contabia-site service (FastAPI, apps/api/main.py)
        │  POST /v1/chat/completions  (bearer = HERMES_CHAT_KEY)
        │  via Railway private network
        ▼
astonishing-nourishment  ──  this gateway (Hermes api_server, hermes-agent 0.19.0)
        │  OpenRouter (deepseek/deepseek-v4-flash)
        ▼
      reply
```

- **Multiplexing is OFF** (`gateway.multiplex_profiles: false`). One profile serves
  the API on the container's `$PORT`. Endpoints are at `/v1/...` — **no** `/p/<profile>/` prefix.
- The gateway container is deliberately minimal: `terminal: none`, no browser,
  no databases. It relays chat turns; it does not have access to accounting data.

## Railway layout

| Resource | Value |
|---|---|
| Project | `intelligent-ambition` |
| Gateway service | `astonishing-nourishment` |
| Gateway public URL | `https://astonishing-nourishment-production-9631.up.railway.app` |
| Gateway private URL | `http://astonishing-nourishment.railway.internal:8080` |
| Backend service | `contabia-site` (FastAPI) → `api.contabia.co` |
| GitHub repo | `TheKevSho/contabia-site` (this service builds from `gateway/`) |

### Env vars — gateway (`astonishing-nourishment`)
```env
API_SERVER_KEY=<strong secret, ≥16 chars; the API server refuses to start without it>
OPENROUTER_API_KEY=<OpenRouter key with credit; upstream 401 "User not found" = out of credit>
```
`start.sh` maps Railway's `$PORT` → `API_SERVER_PORT` and binds `0.0.0.0`.

### Env vars — backend (`contabia-site`)
```env
HERMES_CHAT_URL=http://astonishing-nourishment.railway.internal:8080/v1/chat/completions
HERMES_CHAT_FALLBACK_URL=https://astonishing-nourishment-production-9631.up.railway.app/v1/chat/completions
HERMES_CHAT_KEY=<MUST equal the gateway's API_SERVER_KEY, or every call 401s>
```

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Builds Hermes. **Installs `hermes-agent[messaging]`** — the `messaging` extra pulls `aiohttp`, which the api_server adapter requires. A bare install silently omits it and the gateway 502s. |
| `start.sh` | Writes per-profile `.env` from Railway vars, maps `$PORT`, runs `hermes gateway run`. |
| `config/hermes/config.yaml` | Top-level config: OpenRouter model, `multiplex_profiles: false`, `platforms.api_server.enabled: true`. |
| `config/hermes/profiles/business/config.yaml` | Default profile. |
| `config/hermes/profiles/tayrona/config.yaml` | Tayrona profile (source tag). |

## Health & smoke test

```bash
# Health
curl -s "https://astonishing-nourishment-production-9631.up.railway.app/health"
# → {"status":"ok","platform":"hermes-agent","version":"0.19.0"}

# Authenticated agent turn
curl -s -X POST \
  "https://astonishing-nourishment-production-9631.up.railway.app/v1/chat/completions" \
  -H "Authorization: Bearer $API_SERVER_KEY" -H "Content-Type: application/json" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"ping"}],"stream":false}'

# Full portal path (needs a portal login token from POST /auth/login)
curl -s -X POST "https://api.contabia.co/entities/sonata-001/chat" \
  -H "Authorization: Bearer $PORTAL_TOKEN" -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" -H "Origin: https://app.contabia.co" \
  -d '{"message":"¿Quién eres?","lang":"es"}'
```

## Operating notes

- **Railway CLI:** `npm i -g @railway/cli`, then `railway login` (device code).
  Link with `railway link --project intelligent-ambition --environment production --service <svc>`.
  Read vars: `railway variables --service <svc> --kv`. Set: `railway variables --service <svc> --set K=V`.
- Changing a var triggers a redeploy unless you pass `--skip-deploys`; force one with `railway redeploy --service <svc> --yes`.
- The gateway agent has **no accounting-data access** by design. Answering
  data questions (e.g. "what were June sales") requires wiring the agent to
  Tayrona's Alegra data — not yet built. See the portal chat proxy in
  `apps/api/main.py` (`portal_chat`, ~line 666); it currently sends only a
  system prompt + the user message.

---

## Troubleshooting history — the 502 (resolved 2026-08-30)

Every request (even `/health`) returned `502 Application failed to respond`.
Three independent causes, fixed in order:

1. **api_server never enabled.** `platforms.api_server.enabled` was absent, so the
   gateway ran cron-only and bound no HTTP port. → added `enabled: true`.
2. **aiohttp missing (the real blocker).** `pip install hermes-agent==0.19.0` with no
   extras omits `aiohttp`; logs showed `API Server: aiohttp not installed` →
   `No adapter available for api_server`. → `hermes-agent[messaging]==0.19.0`.
3. **Portal wiring wrong.** `HERMES_CHAT_URL` still carried the `/p/tayrona/` multiplex
   prefix, and `HERMES_CHAT_KEY` didn't match the gateway's `API_SERVER_KEY`.
   → dropped the prefix in `main.py` defaults + Railway var; matched the key.

A fourth, non-code issue surfaced once the gateway came up: OpenRouter returned
`401 User not found` (account out of credit). Resolved by topping up.

Relevant commits: `717a1d1` (enable api_server, drop prefix), `4468279`
(Dockerfile aiohttp extra).
