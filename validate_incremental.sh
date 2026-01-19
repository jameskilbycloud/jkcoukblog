#!/bin/bash
# Validate Incremental Build System
# Run this to verify incremental builds are working with your real WordPress site

set -e

echo "🔍 Incremental Build Validation"
echo "================================"
echo ""

# Check if WP_AUTH_TOKEN is set
if [ -z "$WP_AUTH_TOKEN" ]; then
    echo "❌ Error: WP_AUTH_TOKEN not set"
    echo "   Set it with: export WP_AUTH_TOKEN=\"your_token_here\""
    exit 1
fi

echo "✅ WP_AUTH_TOKEN is set"
echo ""

# Step 1: Check current cache state
echo "Step 1: Checking current cache state..."
echo "----------------------------------------"
python3 scripts/manage_build_cache.py stats
echo ""

# Step 2: Check if cache file exists
if [ -f ".build-cache.json" ]; then
    echo "✅ Cache file exists (.build-cache.json)"
    CACHE_SIZE=$(du -h .build-cache.json | cut -f1)
    echo "   Size: $CACHE_SIZE"
    
    # Show when last build was
    LAST_BUILD=$(python3 -c "import json; data=json.load(open('.build-cache.json')); print(data.get('last_build_time', 'Never'))")
    echo "   Last build: $LAST_BUILD"
    echo ""
    
    # Ask if user wants to test incremental
    echo "📝 You have an existing cache."
    echo "   Next build will be INCREMENTAL (only changed content)"
    echo ""
    read -p "Run an incremental build now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Step 2: Running incremental build..."
        echo "----------------------------------------"
        echo "⏱️  Timing build..."
        echo ""
        
        time python3 scripts/wp_to_static_generator.py ./public
        
        echo ""
        echo "Step 3: Verifying incremental build worked..."
        echo "----------------------------------------"
        python3 scripts/manage_build_cache.py stats
        echo ""
        
        echo "✅ Validation complete!"
        echo ""
        echo "Look for these SUCCESS indicators:"
        echo "  ✓ Build took 2-5 seconds (not 12+ seconds)"
        echo "  ✓ Output said 'Mode: Incremental'"
        echo "  ✓ Output showed '⚡ Time saved vs full build'"
        echo "  ✓ Cache 'Last build' timestamp updated above"
    fi
    
else
    echo "ℹ️  No cache file found (.build-cache.json)"
    echo "   Next build will be FULL BUILD (create cache)"
    echo ""
    
    read -p "Run a full build to create cache? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Step 2: Running FIRST build (creating cache)..."
        echo "----------------------------------------"
        echo "⏱️  This will take ~12 seconds..."
        echo ""
        
        time python3 scripts/wp_to_static_generator.py ./public
        
        echo ""
        echo "Step 3: Verifying cache was created..."
        echo "----------------------------------------"
        
        if [ -f ".build-cache.json" ]; then
            echo "✅ Cache created successfully!"
            python3 scripts/manage_build_cache.py stats
            echo ""
            
            echo "Step 4: Test incremental build..."
            echo "----------------------------------------"
            read -p "Run immediate second build to test incremental? (y/n) " -n 1 -r
            echo ""
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo ""
                echo "⏱️  Timing incremental build (should be ~2-3 seconds)..."
                echo ""
                
                time python3 scripts/wp_to_static_generator.py ./public
                
                echo ""
                echo "✅ INCREMENTAL BUILD TEST COMPLETE!"
                echo ""
                echo "Did you see:"
                echo "  ✓ Second build took only 2-3 seconds? (vs 12s)"
                echo "  ✓ Output said 'Mode: Incremental'?"
                echo "  ✓ Output showed 'Time saved vs full build: ~75%'?"
                echo ""
                echo "If YES to all: ✅ Incremental builds are working!"
                echo "If NO to any: ❌ Something may be wrong"
            fi
        else
            echo "❌ Cache file was NOT created!"
            echo "   Check build output for errors"
        fi
    fi
fi

echo ""
echo "📚 Additional validation commands:"
echo "   python3 scripts/manage_build_cache.py inspect   # Detailed cache view"
echo "   python3 scripts/manage_build_cache.py clear     # Force full rebuild"
echo "   python3 scripts/test_incremental_build.py       # Run automated tests"
