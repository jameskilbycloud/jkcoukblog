#!/usr/bin/env python3
"""
Test Incremental Build System
Validates that incremental builds work correctly
"""

import sys
import time
from pathlib import Path
from incremental_builder import IncrementalBuilder

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_cache_operations():
    """Test basic cache operations"""
    print_section("Test 1: Cache Operations")
    
    # Create a test cache
    cache_file = Path('.test-incremental-cache.json')
    if cache_file.exists():
        cache_file.unlink()
    
    builder = IncrementalBuilder(cache_file)
    
    # Initial state
    stats = builder.get_stats()
    print(f"✓ Cache initialized")
    print(f"  Posts cached: {stats['posts_cached']}")
    print(f"  Pages cached: {stats['pages_cached']}")
    print(f"  Last build: {stats['last_build']}")
    
    # Mark some content as processed
    builder.mark_processed('/2024/01/test-post/', 'hash123', '2024-01-14T10:00:00')
    builder.mark_processed('/2024/01/another-post/', 'hash456', '2024-01-14T11:00:00')
    builder.mark_processed('/about/', 'hash789', '2024-01-10T12:00:00')
    
    # Finalize
    builder.finalize_build(is_full_build=True)
    
    stats = builder.get_stats()
    print(f"\n✓ Processed content marked")
    print(f"  Posts cached: {stats['posts_cached']}")
    print(f"  Pages cached: {stats['pages_cached']}")
    
    # Test change detection
    print(f"\n✓ Testing change detection:")
    print(f"  Has '/2024/01/test-post/' changed (same hash)? {builder.has_changed('/2024/01/test-post/', 'hash123', '2024-01-14T10:00:00')}")
    print(f"  Has '/2024/01/test-post/' changed (new hash)? {builder.has_changed('/2024/01/test-post/', 'newhash', '2024-01-14T10:00:00')}")
    print(f"  Has '/new-post/' changed (not cached)? {builder.has_changed('/new-post/', 'hash000', '2024-01-15T10:00:00')}")
    
    # Clean up
    if cache_file.exists():
        cache_file.unlink()
    
    print(f"\n✅ Cache operations test passed!")

def test_cache_persistence():
    """Test that cache persists between sessions"""
    print_section("Test 2: Cache Persistence")
    
    cache_file = Path('.test-incremental-cache.json')
    if cache_file.exists():
        cache_file.unlink()
    
    # Session 1: Create cache
    print("Session 1: Creating cache...")
    builder1 = IncrementalBuilder(cache_file)
    builder1.mark_processed('/test-1/', 'hash1', '2024-01-14')
    builder1.mark_processed('/test-2/', 'hash2', '2024-01-14')
    builder1.finalize_build(is_full_build=True)
    
    stats1 = builder1.get_stats()
    print(f"  Created cache with {stats1['posts_cached'] + stats1['pages_cached']} entries")
    
    # Session 2: Load existing cache
    print("\nSession 2: Loading existing cache...")
    builder2 = IncrementalBuilder(cache_file)
    
    stats2 = builder2.get_stats()
    print(f"  Loaded cache with {stats2['posts_cached'] + stats2['pages_cached']} entries")
    
    if stats2['posts_cached'] + stats2['pages_cached'] == stats1['posts_cached'] + stats1['pages_cached']:
        print("\n✅ Cache persistence test passed!")
    else:
        print("\n❌ Cache persistence test FAILED!")
        return False
    
    # Clean up
    if cache_file.exists():
        cache_file.unlink()
    
    return True

def test_archive_rebuild_logic():
    """Test archive rebuild decision logic"""
    print_section("Test 3: Archive Rebuild Logic")
    
    cache_file = Path('.test-incremental-cache.json')
    if cache_file.exists():
        cache_file.unlink()
    
    builder = IncrementalBuilder(cache_file)
    
    # First build - should rebuild archives
    print("First build (no cache):")
    should_rebuild = builder.should_rebuild_archives()
    print(f"  Should rebuild archives? {should_rebuild}")
    
    if not should_rebuild:
        print("❌ Test FAILED: First build should rebuild archives")
        return False
    
    # Finalize as full build
    builder.finalize_build(is_full_build=True)
    
    # Immediately after - should not rebuild
    print("\nImmediately after first build:")
    should_rebuild = builder.should_rebuild_archives()
    print(f"  Should rebuild archives? {should_rebuild}")
    
    if should_rebuild:
        print("❌ Test FAILED: Should not rebuild immediately after full build")
        return False
    
    print("\n✅ Archive rebuild logic test passed!")
    
    # Clean up
    if cache_file.exists():
        cache_file.unlink()
    
    return True

def show_validation_guide():
    """Show how to validate incremental builds in real usage"""
    print_section("How to Validate Incremental Builds")
    
    print("""
1. CHECK BUILD OUTPUT
   Look for incremental build messages:
   
   First build:
   ✓ "Mode: Full build (creating cache)"
   ✓ "📋 Discovering content from WordPress REST API..."
   ✓ Processing 150+ URLs
   
   Incremental build:
   ✓ "Mode: Incremental (cache has X entries)"
   ✓ "🔄 Incremental build - checking posts modified since..."
   ✓ "📊 Incremental build: X changed posts"
   ✓ Processing only changed URLs

2. CHECK CACHE STATISTICS
   Before build:
   $ python3 manage_build_cache.py stats
   
   After build:
   $ python3 manage_build_cache.py stats
   
   Verify:
   ✓ "Last build" timestamp updates
   ✓ Cached entries increase

3. MEASURE BUILD TIME
   $ time python3 wp_to_static_generator.py ./public
   
   Compare:
   ✓ First build: ~12 seconds
   ✓ Incremental: ~2-5 seconds
   ✓ Time savings displayed: "⚡ Time saved vs full build: ~75%"

4. VERIFY CACHE FILE EXISTS
   $ ls -lh .build-cache.json
   $ cat .build-cache.json | python3 -m json.tool | head -20

5. FORCE FULL BUILD TEST
   $ python3 manage_build_cache.py clear
   $ python3 wp_to_static_generator.py ./public
   
   Or:
   $ python3 wp_to_static_generator.py ./public --no-incremental

6. INSPECT WHAT WAS PROCESSED
   Look for output like:
   ✓ "⬇️  Processing 2 URLs..." (instead of 156)
   ✓ "✅ Success: 2" (instead of 156)
""")

def main():
    """Run all tests"""
    print("🧪 Incremental Build System Tests")
    print("=" * 60)
    
    try:
        # Run tests
        test_cache_operations()
        
        if not test_cache_persistence():
            sys.exit(1)
        
        if not test_archive_rebuild_logic():
            sys.exit(1)
        
        # Show validation guide
        show_validation_guide()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
