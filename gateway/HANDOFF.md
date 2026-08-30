# 🚀 ContabIA Portal Chat Gateway — Deployment Handoff

> **Date:** August 30, 2026
> **Status:** ✅ **RESOLVED — gateway live, full E2E verified.**
> **Project:** [intelligent-ambition](https://railway.app/project/9cec2b50-4efd-44c1-93a6-65098240d605) (Railway)
> **Gateway service:** `astonishing-nourishment`

---

## ✅ Resolution (2026-08-30)

The 502 had **three** independent root causes, fixed in order:

1. **`config.yaml` never enabled the API server.** `platforms.api_server.enabled` was absent, so the gateway booted for cron only and bound no HTTP port → Railway healthcheck 502. Fixed: added `platforms.api_server.enabled: true` (port/host come from `$PORT` → `API_SERVER_PORT` mapping in `start.sh`, host `0.0.0.0`).
2. **`aiohttp` was not installed in the container (the real blocker).** Dockerfile ran `pip install hermes-agent==0.19.0` with no extras; the API-server adapter requires `aiohttp`, which only ships under an extra. Deploy logs showed `API Server: aiohttp not installed` → `No adapter available for api_server`. Fixed: `pip install "hermes-agent[messaging]==0.19.0"` (the `messaging` extra pins `aiohttp==3.14.1`).
3. **Portal → gateway wiring used the old multiplex prefix + a mismatched key.** `main.py` default `HERMES_CHAT_URL` still had `/p/tayrona/`; the `contabia-site` Railway var still had `/p/tayrona/` AND a `HERMES_CHAT_KEY` that did not match the gateway's `API_SERVER_KEY`. With `multiplex_profiles: false`, the correct path is `/v1/chat/completions` (no prefix). Fixed both the code default and the Railway vars.

A fourth issue surfaced only after the gateway came up: the gateway's **OpenRouter account was out of credits** (`HTTP 401: User not found` from upstream). Resolved by topping up the OpenRouter account (key unchanged, ends `…cc2953`).

### Commits
- `717a1d1` — enable api_server, drop `/p/tayrona/` from `main.py` defaults, fix `start.sh` banner
- `4468279` — Dockerfile `hermes-agent[messaging]` for aiohttp

### Railway vars now set on `contabia-site`
```env
HERMES_CHAT_KEY=<matches astonishing-nourishment API_SERVER_KEY, ends …009f2b2>
HERMES_CHAT_URL=http://astonishing-nourishment.railway.internal:8080/v1/chat/completions
HERMES_CHAT_FALLBACK_URL=https://astonishing-nourishment-production-9631.up.railway.app/v1/chat/completions
```
(Gateway listens on Railway `$PORT` = 8080 internally; public healthcheck via the `.up.railway.app` domain.)

### Verification (all real responses)
- `GET /health` → `200 {"status":"ok","platform":"hermes-agent","version":"0.19.0"}`
- `POST /v1/chat/completions` (Bearer API_SERVER_KEY) → `200`, agent replied `PONG`, `finish_reason: stop`, 9820 tokens
- `POST https://api.contabia.co/entities/sonata-001/chat` (kevin bearer) → `200`, reply: *"Soy el agente ContabIA de Tayrona Sailing (Sonata Mas SAS, NIT 901528910)."*, `source: tayrona`
- `app.contabia.co/chat.html` UI calls this exact endpoint; it is gated by Cloudflare Access (human email-OTP) so was not driven headlessly, but the API path it invokes is fully proven.

---

## 🎯 Goal (original)

Allow the portal chat agent (at `https://app.contabia.co`) to query Tayrona's Hermes profile via a Railway-deployed gateway service, replacing the local `127.0.0.1:8642` Hermes API server. The portal already has the code to point at the gateway — just needs a working endpoint.

---

## 📦 What Exists

### Railway

| Resource | Value |
|---|---|
| **Project** | `intelligent-ambition` (only project with gateway services) |
| **Gateway service** | `astonishing-nourishment` |
| **Gateway domain** | `https://astonishing-nourishment-production-9631.up.railway.app` |
| **GitHub repo** | `TheKevSho/contabia-site` (root dir = `gateway/`) |
| **Other projects** | `soothing-fulfillment` (pre-existing, unrelated) |

### Env vars set on gateway service (Raw Editor, Variables tab)

```env
API_SERVER_KEY=<set — ask Kevin for value>
OPENROUTER_API_KEY=<set — ask Kevin for value>
```

### Env vars on `contabia-site` service (already set)

```env
HERMES_CHAT_URL=https://astonishing-nourishment-production-9631.up.railway.app/p/tayrona/v1/chat/completions
HERMES_CHAT_KEY=<same as API_SERVER_KEY — ask Kevin>
```

> **⚠️  Note:** Now that multiplexing is disabled, the URL path will need to change to:
> `https://astonishing-nourishment-production-9631.up.railway.app/v1/chat/completions`

### Local config files (all committed & pushed)

| File | Purpose |
|---|---|
| `gateway/config/hermes/config.yaml` | Top-level Hermes config. Api key refs, OpenRouter model, `multiplex_profiles: false` |
| `gateway/config/hermes/profiles/tayrona/config.yaml` | Tayrona profile — tools (web, terminal, imessage), source tag, no api_server platform |
| `gateway/config/hermes/profiles/business/config.yaml` | Business profile — tools, same fix |
| `gateway/Dockerfile` | Builds Hermes, copies config, runs `start.sh` |
| `gateway/start.sh` | `hermes serve --profiles business,tayrona` |

### Git history (relevant commits)

```
630fd1f fix: disable multiplex_profiles to resolve gateway startup crash
4a906da fix: disable api_server platform on secondary gateway profiles to allow multiplexing
accb125 fix: install hermes-agent from PyPI (pre-built wheel) instead of git+https
71b38bf gateway: hermes-gateway Dockerfile + config for Railway deployment
b1926f5 chat: route portal -> Tayrona profile directly
```

### Portal code (chat proxy)

Location: `apps/api/main.py` lines 630–730

- `HERMES_CHAT_URL` — env-configured target URL (with fallback)
- `HERMES_CHAT_KEY` — Bearer token sent as `Authorization` header
- Posts to OpenAI-compatible `/v1/chat/completions` endpoint
- Sends `X-Hermes-Session-Id` and `X-Hermes-Session-Key` for session continuity

---

## 🔴 Current Block: 502 Bad Gateway

**Symptom:** Every HTTP request (even `/health`) returns `502 Application failed to respond`.

### Root cause identified

The Hermes process starts but crashes when it tries to multiplex profiles. Each secondary profile had `api_server` enabled (which binds to a port), conflicting with `gateway.multiplex_profiles: true`.

**Fix applied (committed `630fd1f`):** Disabled `multiplex_profiles` in top-level config. Now only the **default profile** serves requests, which is the `business` profile (first in the list).

**What's still unclear:**
3. The Railway **redeploy has not yet completed** with the latest commit. Check Deployments tab in Railway dashboard for `630fd1f` to be active.
4. Even after `630fd1f` deploys, the gateway may still fail if Hermes can't initialize in Railway's environment (pip install, model loading, port binding).

### To resume — verify gateway

```bash
# 1. Wait for redeploy to complete, then test
curl -s -w "\nHTTP_CODE:%{http_code}" \
  "https://astonishing-nourishment-production-9631.up.railway.app/health"

# 2. Try the chat endpoint (without /p/tayrona/ prefix since multiplex is off)
curl -s -w "\nHTTP_CODE:%{http_code}" \
  "https://astonishing-nourishment-production-9631.up.railway.app/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "x-api-key: <API_SERVER_KEY>" \
  -d '{"messages":[{"role":"user","content":"ping"}],"model":"deepseek/deepseek-v4-flash"}'

# 3. If still 502 — check Railway logs for the ACTIVE deployment (not stale)
#    Logs tab → filter for ERROR, WARNING, or crash traces
```

---

## 🔧 How to Debug (if 502 persists)

### Railway-specific troubleshooting

1. **Check Logs tab** in the gateway service page — look for:
   - Python/startup errors
   - `pip install` failures
   - Port binding errors (`address already in use`)
   - Missing env vars

2. **Console tab** — run inside the container:
   ```bash
   ps aux
   ss -tlnp
   cat /proc/1/cmdline
   ```

3. **Deployments tab** — confirm the latest commit `630fd1f` is the ACTIVE deployment

4. **Common Hermes-on-Railway failure modes:**
   - Python version mismatch (Railway default ≠ Hermes requirement)
   - PyPI install timeout (Hermes has many deps)
   - Missing `gcc`/build tools for binary wheels
   - Port not being `$PORT` (Railway injects `$PORT`, Hermes must listen on it)

### If gateway works

1. **Update portal HERMES_CHAT_URL** to remove `/p/tayrona/` prefix:
   ```bash
   # In Railway dashboard → contabia-site → Variables → Raw Editor
   HERMES_CHAT_URL=https://astonishing-nourishment-production-9631.up.railway.app/v1/chat/completions
   ```
2. **Redeploy contabia-site** after env var change
3. **Test end-to-end:** Open `https://app.contabia.co` → login → navigate to Tayrona entity → chat → send a message

---

## ✅ What Was Cleaned

| Check | Status |
|---|---|
| Temp files (`/tmp/*`) | None created, none left |
| Stale Railway services | Two accidental duplicates (`clever-art`, `enthusiastic-quietude`) discarded |
| Git dirty state | Clean — all changes committed and pushed |
| Unused files | None |

---

## 📎 Links & References

| Resource | Link |
|---|---|
| Railway Project | [intelligent-ambition](https://railway.app/project/9cec2b50-4efd-44c1-93a6-65098240d605) |
| Gateway service | `astonishing-nourishment` in project above |
| Gateway URL | `https://astonishing-nourishment-production-9631.up.railway.app` |
| GitHub repo | `TheKevSho/contabia-site` → `gateway/` directory |
| Portal | `https://app.contabia.co` |
| Local repo | `~/src/contabia-site/` |

---

## 📝 Prewritten Resume Prompt

Copy this into your next Hermes session to resume:

```
Resume contabia-site gateway deployment handoff from ~/src/contabia-site/gateway/HANDOFF.md. 
Gateway at intelligent-ambition Railway project, service astonishing-nourishment. 
Last status: 502, config fix committed (630fd1f — multiplex_profiles: false) but redeploy not yet verified. 
Start by reading HANDOFF.md, checking Railway logs, and getting the gateway working. 
Then update portal HERMES_CHAT_URL to remove /p/tayrona/ prefix and redeploy contabia-site. 
End-to-end test via app.contabia.co portal→Tayrona→chat.
```

---

*Handoff prepared by Hermes Agent on behalf of Kevin — August 30, 2026.*