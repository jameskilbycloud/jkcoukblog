#!/usr/bin/env python3
"""
Test that CSP headers allow Credly certification badges to load.
Validates Worker template has correct CSP configuration for Credly embeds.
"""

import sys
import re
from pathlib import Path


def test_worker_csp_credly():
    """Test that _worker.template.js has CSP allowing Credly badges."""
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

    print("🔍 Checking CSP for Credly badge compatibility...\n")

    errors = []

    # Check script-src includes cdn.credly.com and cdn.youracclaim.com
    if 'script-src' in csp:
        script_src = re.search(r'script-src\s+([^;]+)', csp)
        if script_src:
            directives = script_src.group(1)
            if 'cdn.credly.com' not in directives:
                errors.append("script-src missing 'cdn.credly.com'")
            else:
                print("✅ script-src allows cdn.credly.com")

            if 'cdn.youracclaim.com' not in directives:
                errors.append("script-src missing 'cdn.youracclaim.com'")
            else:
                print("✅ script-src allows cdn.youracclaim.com")
        else:
            errors.append("Could not parse script-src directive")
    else:
        errors.append("No script-src directive found")

    # Check frame-src includes www.credly.com and www.youracclaim.com
    if 'frame-src' in csp:
        frame_src = re.search(r'frame-src\s+([^;]+)', csp)
        if frame_src:
            directives = frame_src.group(1)
            if 'www.credly.com' not in directives:
                errors.append("frame-src missing 'https://www.credly.com'")
            else:
                print("✅ frame-src allows www.credly.com")

            if 'www.youracclaim.com' not in directives:
                errors.append("frame-src missing 'https://www.youracclaim.com'")
            else:
                print("✅ frame-src allows www.youracclaim.com")
        else:
            errors.append("Could not parse frame-src directive")
    else:
        errors.append("No frame-src directive found (required for Credly badge iframes)")

    # Print results
    if errors:
        print(f"\n❌ CSP has {len(errors)} issue(s):")
        for error in errors:
            print(f"  - {error}")
        print("\n⚠️  Credly certification badges will be blocked by CSP!")
        print("   The embed.js script and badge iframes will not load.")
        return False
    else:
        print("\n✅ CSP correctly configured for Credly badges!")
        print("   Both cdn.credly.com/cdn.youracclaim.com scripts and badge iframes are allowed.")
        return True


if __name__ == "__main__":
    success = test_worker_csp_credly()
    sys.exit(0 if success else 1)
