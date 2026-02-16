#!/usr/bin/env python3
"""
Test that CSP headers allow Utterances to load.
Validates Worker template has correct CSP configuration.
"""

import sys
import re
from pathlib import Path


def test_worker_csp():
    """Test that _worker.template.js has CSP allowing Utterances."""
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

    print("🔍 Checking CSP for Utterances compatibility...\n")

    errors = []

    # Check script-src includes utteranc.es
    if 'script-src' in csp:
        script_src = re.search(r'script-src\s+([^;]+)', csp)
        if script_src:
            directives = script_src.group(1)
            if 'utteranc.es' not in directives:
                errors.append("script-src missing 'https://utteranc.es'")
            else:
                print("✅ script-src allows utteranc.es")
        else:
            errors.append("Could not parse script-src directive")
    else:
        errors.append("No script-src directive found")

    # Check frame-src exists and includes utteranc.es
    if 'frame-src' in csp:
        frame_src = re.search(r'frame-src\s+([^;]+)', csp)
        if frame_src:
            directives = frame_src.group(1)
            if 'utteranc.es' not in directives:
                errors.append("frame-src missing 'https://utteranc.es'")
            else:
                print("✅ frame-src allows utteranc.es")
        else:
            errors.append("Could not parse frame-src directive")
    else:
        errors.append("No frame-src directive found (required for Utterances iframe)")

    # Check connect-src includes GitHub API
    if 'connect-src' in csp:
        connect_src = re.search(r'connect-src\s+([^;]+)', csp)
        if connect_src:
            directives = connect_src.group(1)
            if 'api.github.com' not in directives:
                errors.append("connect-src missing 'https://api.github.com'")
            else:
                print("✅ connect-src allows api.github.com")
        else:
            errors.append("Could not parse connect-src directive")
    else:
        errors.append("No connect-src directive found")

    # Print results
    if errors:
        print(f"\n❌ CSP has {len(errors)} issue(s):")
        for error in errors:
            print(f"  - {error}")
        print("\n⚠️  Utterances will be blocked by CSP!")
        print("   Users will see CSP violation errors in browser console.")
        return False
    else:
        print("\n✅ CSP correctly configured for Utterances!")
        print("   Utterances script, iframe, and GitHub API are all allowed.")
        return True


if __name__ == "__main__":
    success = test_worker_csp()
    sys.exit(0 if success else 1)
