import json
import uuid
import re
import sys
from typing import Any, Dict

import requests

"""
If you recieve 403 forbidden its a simple CF Block just use import tls_client, and use it as requests.session()

session = tls_client.Session(
    client_identifier="chrome112",
    random_tls_extension_order=True
)

-> https://github.com/FlorianREGAZ/Python-Tls-Client
"""


USERNAME = "alice" 
API      = "https://api.wallet.coinbase.com"
ENDPOINT = f"{API}/rpc/v2/getPublicProfileByDomain"

def normalize_username(username: str) -> str:
    username = username.strip().lower()

    if username.endswith(".cb.id"):
        username = username[:-6]

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", username):
        raise ValueError(
            "Invalid username format. Use only the cb.id label, for example: alice"
        )

    return username


def fetch_public_profile(username: str) -> Dict[str, Any]:
    user_domain = f"{username}.cb.id"

    
    headers = {
        "Host": "api.wallet.coinbase.com",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "X-Cb-Session-Uuid": str(uuid.uuid4()),
        "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138"',
        "X-Cb-Platform": "extension",
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Appsflyer-Id": "",
        "X-Cb-Ujs": "",
        "X-Cb-Version-Name": "3.123.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Cb-Is-Logged-In": "true",
        "X-Platform-Name": "extension",
        "X-Cb-Device-Id": str(uuid.uuid4()),
        "X-Cb-Project-Name": "wallet_extension",
        "X-Release-Stage": "production",
        "X-App-Version": "3.123.0",
        "X-Cb-Pagekey": "profile",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Storage-Access": "active",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=1, i",
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
