#!/usr/bin/env python3
"""
Enable Cloudflare Email Routing for asset-energy.ai:
  - MX + SPF DNS records
  - Forward contact@asset-energy.ai -> CONTACT_FORWARD_TO (default: richardcrounse@gmail.com)

Usage:
  export CLOUDFLARE_API_TOKEN="your_token"
  python3 scripts/setup-email-routing.py

Or create Asset-Energy-Web/.env with:
  CLOUDFLARE_API_TOKEN=...
  CONTACT_FORWARD_TO=richardcrounse@gmail.com
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.cloudflare.com/client/v4"
DOMAIN = os.environ.get("DOMAIN", "asset-energy.ai")
FORWARD_TO = os.environ.get("CONTACT_FORWARD_TO", "richardcrounse@gmail.com")
CUSTOM_LOCAL = os.environ.get("CUSTOM_LOCAL_PART", "contact")
CUSTOM_ADDRESS = f"{CUSTOM_LOCAL}@{DOMAIN}"


def load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def request(method: str, path: str, body: dict | None = None) -> dict:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Missing CLOUDFLARE_API_TOKEN.\n"
            "Create a token at https://dash.cloudflare.com/profile/api-tokens\n"
            "Permissions: Zone:Read, DNS:Edit, Email Routing (zone + rules), "
            "Email Routing Addresses:Edit (account).\n"
            "Then: export CLOUDFLARE_API_TOKEN='...' and re-run this script."
        )

    url = f"{API}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} {method} {path}\n{detail}") from exc

    if not payload.get("success"):
        raise SystemExit(f"API error {method} {path}:\n{json.dumps(payload, indent=2)}")
    return payload


def get_zone() -> dict:
    payload = request("GET", f"/zones?name={DOMAIN}&status=active")
    zones = payload.get("result") or []
    if not zones:
        raise SystemExit(f"Zone not found for domain: {DOMAIN}")
    return zones[0]


def enable_email_routing_dns(zone_id: str) -> dict:
    # Adds MX + SPF and enables Email Routing for the zone.
    return request("POST", f"/zones/{zone_id}/email/routing/dns", {"name": DOMAIN})


def get_routing_status(zone_id: str) -> dict:
    payload = request("GET", f"/zones/{zone_id}/email/routing")
    return payload.get("result") or {}


def list_destination_addresses(account_id: str) -> list[dict]:
    payload = request("GET", f"/accounts/{account_id}/email/routing/addresses")
    return payload.get("result") or []


def create_destination_address(account_id: str, email: str) -> dict:
    payload = request(
        "POST",
        f"/accounts/{account_id}/email/routing/addresses",
        {"email": email},
    )
    return payload.get("result") or {}


def ensure_destination_verified(account_id: str, email: str) -> dict:
    for addr in list_destination_addresses(account_id):
        if (addr.get("email") or "").lower() == email.lower():
            if addr.get("verified"):
                print(f"Destination verified: {email}")
                return addr
            print(
                f"Destination exists but NOT verified: {email}\n"
                "Check Gmail for Cloudflare verification email and click the link, then re-run."
            )
            return addr

    print(f"Creating destination address: {email}")
    created = create_destination_address(account_id, email)
    if created.get("verified"):
        print(f"Destination verified: {email}")
    else:
        print(
            f"Verification email sent to {email}.\n"
            "Open it, click Verify, then re-run this script to create the contact@ rule."
        )
    return created


def list_rules(zone_id: str) -> list[dict]:
    payload = request("GET", f"/zones/{zone_id}/email/routing/rules")
    return payload.get("result") or []


def rule_for_contact(rules: list[dict]) -> dict | None:
    for rule in rules:
        for matcher in rule.get("matchers") or []:
            if matcher.get("field") == "to" and matcher.get("value") == CUSTOM_ADDRESS:
                return rule
    return None


def create_contact_rule(zone_id: str, forward_to: str) -> dict:
    body = {
        "name": f"Forward {CUSTOM_ADDRESS}",
        "enabled": True,
        "priority": 0,
        "matchers": [
            {
                "type": "literal",
                "field": "to",
                "value": CUSTOM_ADDRESS,
            }
        ],
        "actions": [
            {
                "type": "forward",
                "value": [forward_to],
            }
        ],
    }
    payload = request("POST", f"/zones/{zone_id}/email/routing/rules", body)
    return payload.get("result") or {}


def verify_mx_records() -> None:
    import subprocess

    print("\nChecking public MX records...")
    proc = subprocess.run(
        ["dig", "@1.1.1.1", "MX", DOMAIN, "+short"],
        capture_output=True,
        text=True,
        check=False,
    )
    mx = proc.stdout.strip()
    if mx:
        print(mx)
    else:
        print("(no MX yet — DNS may need a few minutes to propagate)")


def main() -> None:
    load_dotenv()
    print(f"Domain: {DOMAIN}")
    print(f"Forward: {CUSTOM_ADDRESS} -> {FORWARD_TO}")

    zone = get_zone()
    zone_id = zone["id"]
    account_id = zone["account"]["id"]
    print(f"Zone ID: {zone_id}")

    status = get_routing_status(zone_id)
    if status.get("enabled"):
        print(f"Email Routing already enabled (status: {status.get('status')})")
    else:
        print("Enabling Email Routing DNS (MX + SPF)...")
        result = enable_email_routing_dns(zone_id)
        print(f"Enabled: {json.dumps(result.get('result') or result, indent=2)}")

    dest = ensure_destination_verified(account_id, FORWARD_TO)
    if not dest.get("verified"):
        verify_mx_records()
        raise SystemExit(0)

    rules = list_rules(zone_id)
    existing = rule_for_contact(rules)
    if existing:
        print(f"Routing rule already exists for {CUSTOM_ADDRESS}")
    else:
        print(f"Creating routing rule: {CUSTOM_ADDRESS} -> {FORWARD_TO}")
        created = create_contact_rule(zone_id, FORWARD_TO)
        print(f"Rule created: {created.get('id')}")

    verify_mx_records()
    print("\nDone. Send a test email to", CUSTOM_ADDRESS)


if __name__ == "__main__":
    main()
