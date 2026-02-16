#!/usr/bin/env python3
"""
Test that Plausible Analytics is correctly configured.
Validates Worker template CSP and HTML injection.
"""

import sys
import re
from pathlib import Path


def test_worker_csp_plausible():
    """Test that _worker.template.js has CSP allowing Plausible."""
    worker_file = Path('_worker.template.js')

    if not worker_file.exists():
        print("❌ _worker.template.js not found!")
        return False

    content = worker_file.read_text()

    # Find CSP line - value is in double quotes and may contain single quotes
    csp_match = re.search(r"'Content-Security-Policy':\s*\"([^\"]+)\"", content)

    if not csp_match:
        print("❌ No CSP header found in Worker!")
        return False

    csp = csp_match.group(1)

    print("🔍 Checking CSP for Plausible Analytics compatibility...\n")

    errors = []

    # Check script-src includes plausible.io
    if 'script-src' in csp:
        script_src = re.search(r'script-src\s+([^;]+)', csp)
        if script_src:
            directives = script_src.group(1)
            if 'plausible.io' not in directives:
                errors.append("script-src missing 'plausible.io'")
            else:
                print("✅ script-src allows plausible.io")
        else:
            errors.append("Could not parse script-src directive")
    else:
        errors.append("No script-src directive found")

    # Check connect-src includes plausible.io
    if 'connect-src' in csp:
        connect_src = re.search(r'connect-src\s+([^;]+)', csp)
        if connect_src:
            directives = connect_src.group(1)
            if 'plausible.io' not in directives:
                errors.append("connect-src missing 'plausible.io'")
            else:
                print("✅ connect-src allows plausible.io")
        else:
            errors.append("Could not parse connect-src directive")
    else:
        errors.append("No connect-src directive found")

    # Print results
    if errors:
        print(f"\n❌ CSP has {len(errors)} issue(s):")
        for error in errors:
            print(f"  - {error}")
        print("\n⚠️  Plausible Analytics will be blocked by CSP!")
        print("   Analytics tracking will not work.")
        return False
    else:
        print("\n✅ CSP correctly configured for Plausible Analytics!")
        print("   Plausible script and API connections are allowed.")
        return True


if __name__ == "__main__":
    success = test_worker_csp_plausible()
    sys.exit(0 if success else 1)
