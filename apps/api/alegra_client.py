"""
Alegra API connector.

Corrections applied per Contabia canon File 07 (2026-07-08 live-API research):
  - Journal entries live at /journals (comprobante contable), NOT /journal-entries.
  - There is no bulk/CSV import endpoint for journals - one POST per journal, per line client-side.
  - /payments registers a payment against a bill/invoice (needed for AP/AR exception resolution).
  - Rate limit: 150 req/min per user. Must back off on HTTP 429.

Auth: HTTP Basic — username = Alegra account email, password = Alegra API token.
Both must be supplied via environment variables. Nothing is hardcoded here;
this file is safe to commit.
"""
import os
import time
from typing import Any, Optional

import requests

ALEGRA_BASE_URL = "https://api.alegra.com/api/v1"


class AlegraAuthError(RuntimeError):
    pass


class AlegraClient:
    def __init__(self, email: Optional[str] = None, token: Optional[str] = None):
        self.email = email or os.environ.get("ALEGRA_EMAIL")
        self.token = token or os.environ.get("ALEGRA_API_TOKEN")
        if not self.email or not self.token:
            raise AlegraAuthError(
                "Set ALEGRA_EMAIL and ALEGRA_API_TOKEN env vars (per-client Alegra "
                "Pro/Plus API credentials). Never hardcode these in source."
            )
        self._session = requests.Session()
        self._session.auth = (self.email, self.token)

    def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(self, path: str, json_body: dict[str, Any]) -> Any:
        return self._request("POST", path, json_body=json_body)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json_body: Optional[dict[str, Any]] = None,
        _retry: int = 0,
    ) -> Any:
        url = f"{ALEGRA_BASE_URL}{path}"
        resp = self._session.request(method, url, params=params, json=json_body, timeout=30)
        if resp.status_code == 429 and _retry < 5:
            # Exponential backoff per File 07 (150 req/min limit).
            time.sleep(2**_retry)
            return self._request(method, path, params, json_body, _retry=_retry + 1)
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return None

    # ---- Read endpoints (Monthly Data Pull Sequence, File 07) ----

    def get_accounts(self) -> Any:
        """Chart of accounts + balances = trial balance."""
        return self._get("/accounts")

    def get_journals(self, start: Optional[str] = None, end: Optional[str] = None) -> Any:
        """Existing comprobantes contables. CORRECTED endpoint: /journals, not /journal-entries."""
        params = {}
        if start:
            params["date_start"] = start
        if end:
            params["date_end"] = end
        return self._get("/journals", params=params)

    def get_invoices(self, start: Optional[str] = None, end: Optional[str] = None) -> Any:
        params = {}
        if start:
            params["date_start"] = start
        if end:
            params["date_end"] = end
        return self._get("/invoices", params=params)

    def get_bills(self, start: Optional[str] = None, end: Optional[str] = None) -> Any:
        params = {}
        if start:
            params["date_start"] = start
        if end:
            params["date_end"] = end
        return self._get("/bills", params=params)

    def get_bank_accounts(self) -> Any:
        return self._get("/bank-accounts")

    def get_contacts(self) -> Any:
        return self._get("/contacts")

    # ---- Write endpoints — ONLY called after accountant approval in the portal ----

    def post_journal(self, journal_payload: dict[str, Any]) -> Any:
        """
        Post one approved journal entry (comprobante contable) to /journals.
        journal_payload must already be a balanced entry in Alegra's expected shape
        (see developer.alegra.com). The caller (main.py) enforces that this is only
        ever invoked for exceptions/JEs whose status == 'approved_by_edwin' — the
        motor never posts on its own initiative.
        """
        return self._post("/journals", journal_payload)

    def post_payment(self, payment_payload: dict[str, Any]) -> Any:
        """Register a payment against a bill/invoice — for AP/AR exception resolution."""
        return self._post("/payments", payment_payload)
