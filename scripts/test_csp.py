#!/usr/bin/env python3
"""
Consolidated CSP test — validates that _worker.template.js CSP headers
allow all required third-party services (Utterances, Credly, Plausible).

Usage:
    python3 scripts/test_csp.py              # Test all providers
    python3 scripts/test_csp.py utterances   # Test one provider
    python3 scripts/test_csp.py credly plausible  # Test specific providers
"""

import sys
import re
from pathlib import Path

# Each provider defines which domains must appear in which CSP directives.
PROVIDERS = {
    'utterances': {
        'label': 'Utterances comments',
        'checks': {
            'script-src': ['utteranc.es'],
            'frame-src': ['utteranc.es'],
            'connect-src': ['api.github.com'],
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
        'label': 'Plausible Analytics',
        'checks': {
            'script-src': ['plausible.io', 'plausible.jameskilby.cloud'],
            'connect-src': ['plausible.io', 'plausible.jameskilby.cloud'],
            'frame-src': ['plausible.jameskilby.cloud'],
        },
        'blocked_msg': 'Plausible Analytics will be blocked by CSP!',
        'success_msg': 'CSP correctly configured for Plausible Analytics!',
    },
}


def read_csp():
    """Read and return the CSP string from _worker.template.js."""
    worker_file = Path('_worker.template.js')
    if not worker_file.exists():
        print("❌ _worker.template.js not found!")
        return None

    content = worker_file.read_text()
    csp_match = re.search(r"'Content-Security-Policy':\s*\"([^\"]+)\"", content)
    if not csp_match:
        print("❌ No CSP header found in Worker!")
        return None

    return csp_match.group(1)


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
        print(f"❌ Some CSP checks failed!")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
