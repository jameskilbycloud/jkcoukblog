#!/usr/bin/env python3
"""
Consolidated CSP test — validates that the deployed CSP allows all required
third-party services (Utterances, Credly, Plausible).

The CSP lives in _headers (Cloudflare Pages applies it after the worker, so
that's the source of truth). Validation reads from _headers directly.

Usage:
    python3 scripts/test_csp.py              # Test all providers
    python3 scripts/test_csp.py utterances   # Test one provider
    python3 scripts/test_csp.py credly plausible  # Test specific providers
"""

import sys
import re
from pathlib import Path

# Each provider defines which domains must appear in which CSP directives.
# Only the *parent* page's requirements are enforced here — iframe content
# (e.g. Utterances calling api.github.com from inside its own iframe) is
# governed by the iframe's own CSP, not ours.
PROVIDERS = {
    'utterances': {
        'label': 'Utterances comments',
        'checks': {
            'script-src': ['utteranc.es'],
            'frame-src': ['utteranc.es'],
        },
        'blocked_msg': 'Utterances will be blocked by CSP!',
        'success_msg': 'CSP correctly configured for Utterances!',
    },
    'credly': {
        'label': 'Credly certification badges',
        'checks': {
            'script-src': ['cdn.credly.com', 'cdn.youracclaim.com'],
            'frame-src': ['www.credly.com', 'www.youracclaim.com'],
        },
        'blocked_msg': 'Credly certification badges will be blocked by CSP!',
        'success_msg': 'CSP correctly configured for Credly badges!',
    },
    'plausible': {
        # This site uses self-hosted Plausible at plausible.jameskilby.cloud
        # (proxied via /js/script.js). plausible.io is not used.
        'label': 'Plausible Analytics',
        'checks': {
            'script-src': ['plausible.jameskilby.cloud'],
            'connect-src': ['plausible.jameskilby.cloud'],
            'frame-src': ['plausible.jameskilby.cloud'],
        },
        'blocked_msg': 'Plausible Analytics will be blocked by CSP!',
        'success_msg': 'CSP correctly configured for Plausible Analytics!',
    },
}


def read_csp():
    """Read and return the CSP string from _headers (root)."""
    headers_file = Path('_headers')
    if not headers_file.exists():
        print("❌ _headers not found!")
        return None

    content = headers_file.read_text()
    # _headers lines look like:  Content-Security-Policy: default-src 'self'; ...
    csp_match = re.search(
        r"^\s*Content-Security-Policy:\s*(.+)$",
        content,
        re.MULTILINE,
    )
    if not csp_match:
        print("❌ No Content-Security-Policy line found in _headers!")
        return None

    return csp_match.group(1).strip()


def check_provider(csp, name):
    """Validate CSP for a single provider. Returns True if all checks pass."""
    provider = PROVIDERS[name]
    print(f"🔍 Checking CSP for {provider['label']}...\n")

    errors = []

    for directive, domains in provider['checks'].items():
        if directive not in csp:
            errors.append(f"No {directive} directive found")
            continue

        match = re.search(rf'{directive}\s+([^;]+)', csp)
        if not match:
            errors.append(f"Could not parse {directive} directive")
            continue

        directive_value = match.group(1)
        for domain in domains:
            if domain not in directive_value:
                errors.append(f"{directive} missing '{domain}'")
            else:
                print(f"  ✅ {directive} allows {domain}")

    if errors:
        print(f"\n  ❌ CSP has {len(errors)} issue(s):")
        for error in errors:
            print(f"    - {error}")
        print(f"\n  ⚠️  {provider['blocked_msg']}")
        return False

    print(f"\n  ✅ {provider['success_msg']}")
    return True


def main():
    providers_to_test = sys.argv[1:] if len(sys.argv) > 1 else list(PROVIDERS.keys())

    for name in providers_to_test:
        if name not in PROVIDERS:
            print(f"❌ Unknown provider: {name}")
            print(f"   Available: {', '.join(PROVIDERS.keys())}")
            sys.exit(1)

    csp = read_csp()
    if csp is None:
        sys.exit(1)

    all_passed = True
    for i, name in enumerate(providers_to_test):
        if i > 0:
            print()
        if not check_provider(csp, name):
            all_passed = False

    if all_passed:
        print(f"\n{'='*50}")
        print(f"✅ All {len(providers_to_test)} CSP check(s) passed!")
    else:
        print(f"\n{'='*50}")
        print("❌ Some CSP checks failed!")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
