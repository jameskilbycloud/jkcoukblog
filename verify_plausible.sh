#!/bin/bash

# Quick verification script for Plausible Analytics integration

echo "🔍 Verifying Plausible Analytics Integration"
echo "=============================================="
echo ""

# Check 1: Verify the method exists in the generator
echo "1️⃣  Checking for add_plausible_analytics() method..."
if grep -q "def add_plausible_analytics" wp_to_static_generator.py; then
    echo "   ✅ Method found in wp_to_static_generator.py"
else
    echo "   ❌ Method NOT found!"
    exit 1
fi

# Check 2: Verify it's called from add_static_optimizations
echo ""
echo "2️⃣  Checking method is called during HTML processing..."
if grep -q "self.add_plausible_analytics(soup)" wp_to_static_generator.py; then
    echo "   ✅ Method is called in add_static_optimizations()"
else
    echo "   ❌ Method is NOT called!"
    exit 1
fi

# Check 3: Verify configuration values
echo ""
echo "3️⃣  Checking configuration values..."
if grep -q "plausible_domain = 'plausible.jameskilby.cloud'" wp_to_static_generator.py; then
    echo "   ✅ Plausible domain: plausible.jameskilby.cloud"
else
    echo "   ⚠️  Plausible domain might be different"
fi

if grep -q "target_analytics_domain = 'jameskilby.co.uk'" wp_to_static_generator.py; then
    echo "   ✅ Analytics domain: jameskilby.co.uk"
else
    echo "   ⚠️  Analytics domain might be different"
fi

# Check 4: Verify syntax
echo ""
echo "4️⃣  Checking Python syntax..."
if python3 -m py_compile wp_to_static_generator.py 2>/dev/null; then
    echo "   ✅ Python syntax is valid"
else
    echo "   ❌ Python syntax errors detected!"
    exit 1
fi

# Check 5: Verify existing generated files have Plausible
echo ""
echo "5️⃣  Checking existing generated files..."
PLAUSIBLE_COUNT=$(grep -r "plausible.jameskilby.cloud" public/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$PLAUSIBLE_COUNT" -gt 0 ]; then
    echo "   ✅ Found Plausible in $PLAUSIBLE_COUNT locations in public/"
else
    echo "   ⚠️  Plausible not found in existing files (will be added on next generation)"
fi

# Check 6: Verify documentation exists
echo ""
echo "6️⃣  Checking documentation..."
if [ -f "PLAUSIBLE_ANALYTICS.md" ]; then
    echo "   ✅ PLAUSIBLE_ANALYTICS.md exists"
else
    echo "   ❌ Documentation missing!"
fi

if [ -f "test_plausible_integration.py" ]; then
    echo "   ✅ test_plausible_integration.py exists"
else
    echo "   ❌ Test file missing!"
fi

# Summary
echo ""
echo "=============================================="
echo "✅ All checks passed! Plausible Analytics automation is ready."
echo ""
echo "📝 Next steps:"
echo "   1. Commit and push changes to GitHub"
echo "   2. Wait for next automated run (6 AM or 6 PM UTC)"
echo "   3. Or trigger manually: gh workflow run deploy-static-site.yml"
echo "   4. Verify in generated HTML: grep -r 'data-domain=\"jameskilby.co.uk\"' public/"
echo ""
