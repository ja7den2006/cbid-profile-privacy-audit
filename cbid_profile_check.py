import json
import re
import sys
from typing import Any, Dict

import requests


USERNAME = "alice" 
API      = "https://api.wallet.coinbase.com"
ENDPOINT = f"{API}/rpc/v2/getPublicProfileByDomain"

def normalize_username(username: str) -> str:
    username = username.strip().lower()

    if username.endswith(".cb.id"):
        username = username[:-6]

    # Conservative username validation for a safe demo.
    # This prevents accidental full URLs, emails, shell content, or file paths.
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", username):
        raise ValueError(
            "Invalid username format. Use only the cb.id label, for example: alice"
        )

    return username


def fetch_public_profile(username: str) -> Dict[str, Any]:
    user_domain = f"{username}.cb.id"

    headers = {
        "Accept": "application/json",
        "User-Agent": "cbid-profile-privacy-audit/1.0",
    }

    response = requests.get(
        ENDPOINT,
        params={"userDomain": user_domain},
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def extract_coin_addresses(data: Dict[str, Any]) -> Dict[str, str]:
    coin_addresses = (
        data.get("result", {})
        .get("subdomainProfile", {})
        .get("coinAddresses", {})
    )

    if not isinstance(coin_addresses, dict):
        return {}

    clean_addresses = {}

    for coin, address in coin_addresses.items():
        if not coin or not address:
            continue

        coin_name = str(coin).strip().lower()
        address_text = str(address).strip()

        if coin_name and address_text:
            clean_addresses[coin_name] = address_text

    return clean_addresses


def main() -> int:
    try:
        username = normalize_username(USERNAME)
        data = fetch_public_profile(username)
        clean_addresses = extract_coin_addresses(data)

        print(json.dumps(clean_addresses, indent=2, sort_keys=True))
        return 0

    except requests.exceptions.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 1

    except requests.exceptions.RequestException as exc:
        print(f"Request error: {exc}", file=sys.stderr)
        return 1

    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 1

    except json.JSONDecodeError:
        print("Response was not valid JSON.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
