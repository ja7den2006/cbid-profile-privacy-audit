# cbid-profile-privacy-audit

A small responsible-disclosure research repo documenting the privacy risks of public `cb.id` profile lookups when a human-readable Coinbase Wallet username exposes multiple asset addresses through a public profile response.

This project is not a Coinbase exploit, credential attack, account-takeover tool, or bulk lookup system. It is a minimal awareness and audit project showing how public wallet profile data can create unexpected correlation risk.

## Summary

Coinbase Wallet `cb.id` usernames are designed to make wallet identities easier to use and share. A username like:

```text
alice.cb.id
```

can resolve to public profile information. Depending on the profile and current endpoint behavior, the response may include a `coinAddresses` object containing addresses for multiple assets or networks.

Example shape:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "subdomainProfile": {
      "username": "alice",
      "domain": "alice.cb.id",
      "coinAddresses": {
        "btc": "bc1q...",
        "eth": "0x7ec...",
        "ltc": "ltc1q...",
        "xrp": "rXYZ..."
      }
    }
  }
}
```

The privacy concern is not that public receiving addresses exist. The concern is that a single, easy-to-guess public handle can potentially expose a multi-asset address map, making cross-chain identity correlation easier than users may expect.

## Endpoint Observed

```text
GET https://api.wallet.coinbase.com/rpc/v2/getPublicProfileByDomain?userDomain={username}.cb.id
```

Observed from the Coinbase Wallet browser extension.

Endpoint behavior, response schema, protections, and visibility rules may change at any time.

## Why This Matters

### 1. Privacy surprise

A user may understand that a public username can receive funds, but may not realize the profile lookup can expose several asset addresses at once.

For example, a user may expect:

```text
alice.cb.id -> ETH receiving address
```

but not expect:

```text
alice.cb.id -> BTC + ETH + LTC + XRP + other addresses
```

Even when this behavior is intentional, users should clearly understand what is public.

### 2. Cross-chain correlation

If one public profile returns multiple addresses, third parties can connect activity across chains more easily.

That can enable:

- Linking separate on-chain histories to one identity
- Building address graphs around one public username
- Combining profile data with public blockchain explorers
- Reducing the privacy benefit of using separate addresses across assets

### 3. Phishing and social-engineering risk

Attackers can make phishing messages more convincing if they can reference public wallet details tied to a username.

For example, a scammer could claim:

```text
We detected an issue with your BTC and ETH wallet addresses linked to alice.cb.id.
```

Even without account access, knowing real public wallet data can make a fake support message feel more believable.

### 4. Username-to-real-identity correlation

A non-random username can sometimes be connected to a real person through reused handles, leaked data, social media, or other public sources.

This repo intentionally does not include email validation, leaked database matching, bulk username generation, or account-existence checking. Those workflows create abuse risk and are out of scope.

## Threat Model

This issue is most relevant when all of the following are true:

1. A user has a public `cb.id` profile.
2. The username is guessable or reused elsewhere.
3. The profile exposes multiple asset addresses.
4. A third party connects the username to an off-chain identity.
5. The third party uses the address data for profiling, targeting, phishing, or harassment.

## What This Project Demonstrates

The included script performs a single lookup for one `cb.id` username and prints non-empty `coinAddresses` values.

It is intended for:

- Checking your own public profile
- Demonstrating the privacy model to security teams
- Supporting a responsible disclosure report
- Educating users about public wallet identity exposure

It is not intended for:

- Bulk enumeration
- Email-to-username matching
- Coinbase account-existence checking
- Bypassing anti-abuse systems
- Phishing, fraud, doxxing, harassment, or targeting users

## Safe Proof of Concept

Install dependencies:

```bash
pip install -r requirements.txt
```

Edit `cbid_profile_check.py`:

```python
USERNAME = "alice"
```

Use your own username or a username you have permission to test.

Run:

```bash
python cbid_profile_check.py
```

Example output:

```json
{
  "btc": "bc1q...",
  "eth": "0x7ec...",
  "ltc": "ltc1q..."
}
```

If no public addresses are exposed, the script prints an empty object:

```json
{}
```

## Responsible Testing Rules

To keep this research safe and reproducible:

- Test only your own `cb.id` username or accounts you have explicit permission to check.
- Do not run bulk lookups.
- Do not combine this with leaked emails, credential dumps, phone numbers, or account-existence checkers.
- Do not bypass rate limits, Cloudflare, bot protection, or other anti-abuse controls.
- Do not publish real third-party usernames, addresses, balances, or identity links.
- Redact all addresses in screenshots and reports unless they belong to you.

## Limitations and Assumptions

- Works only for existing public `cb.id` usernames.
- Nonexistent, private, restricted, or changed profiles may not return addresses.
- Returned keys and addresses depend on profile settings and current Coinbase Wallet behavior.
- Endpoint behavior and schema can change at any time.
- A public address alone does not prove who controls the wallet.
- On-chain balances and activity can be misread without context.
- This project does not test Coinbase account ownership or Coinbase exchange account status.

## Mitigations for Users

Users can reduce correlation risk by:

- Reviewing Coinbase Wallet / `cb.id` profile visibility settings.
- Only exposing addresses they intentionally want public.
- Using dedicated public receiving addresses for tips, donations, or creator profiles.
- Avoiding username reuse between financial profiles and personal accounts.
- Avoiding usernames based on email prefixes, legal names, school usernames, or old leaked handles.
- Treating public wallet usernames as permanent public identity markers.
- Periodically reviewing what third parties can see about their profile.

## Recommendations for Coinbase / Wallet Providers

Possible product and platform improvements:

### Least-surprise defaults

Make multi-asset address visibility opt-in, not assumed.

### Per-asset controls

Let users choose exactly which assets or networks are public.

### Clear public-profile warnings

Show an explicit notice such as:

```text
Anyone can look up this username and view the addresses you mark public.
```

### Preview public profile

Provide a "View as public" screen showing exactly what unauthenticated users can see.

### Anti-enumeration controls

Use rate limiting, telemetry, abuse detection, and progressive friction against automated lookup patterns.

### Response minimization

Return only fields the user explicitly marked public. Avoid empty or unnecessary fields.

### Safer defaults for new users

For new usernames, expose the minimum needed for receiving funds and prompt users before adding additional assets.

> I observed that a public Coinbase Wallet `cb.id` profile lookup can return a multi-asset `coinAddresses` map for a username. While public wallet naming may be expected behavior, the current visibility model may create a privacy surprise for users who do not realize multiple asset addresses are publicly resolvable through one unauthenticated profile endpoint. This can increase cross-chain correlation and phishing risk when usernames are reused or guessable. I recommend clearer public-profile warnings, per-asset visibility controls, and anti-enumeration protections.

## Repo Scope

This repository is limited to documentation and a single-profile checker.

No bypass code, scraping framework, mass checker, account checker, leaked-data workflow, or phishing tooling will be added.

## References

- Coinbase Help: Coinbase ENS / `cb.id` username support
- Coinbase Help: Sending and receiving crypto through Coinbase Wallet
- ENS public naming concepts and Coinbase / ENS integration materials

## License

MIT License. See `LICENSE`.
