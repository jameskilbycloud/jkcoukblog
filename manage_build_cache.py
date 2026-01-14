#!/usr/bin/env python3
"""
Build Cache Management Tool
Manage the incremental build cache
"""

import sys
from pathlib import Path
from incremental_builder import IncrementalBuilder
from datetime import datetime

def print_stats(builder):
    """Print cache statistics"""
    stats = builder.get_stats()
    
    print("📊 Build Cache Statistics")
    print("=" * 60)
    print(f"Posts cached:      {stats['posts_cached']}")
    print(f"Pages cached:      {stats['pages_cached']}")
    print(f"Assets cached:     {stats['assets_cached']}")
    print(f"Total entries:     {stats['posts_cached'] + stats['pages_cached'] + stats['assets_cached']}")
    
    if stats['last_build']:
        try:
            last_build = datetime.fromisoformat(stats['last_build'])
            time_ago = datetime.now() - last_build
            hours = time_ago.total_seconds() / 3600
            
            if hours < 1:
                minutes = int(time_ago.total_seconds() / 60)
                time_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif hours < 24:
                time_str = f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
            else:
                days = int(hours / 24)
                time_str = f"{days} day{'s' if days != 1 else ''} ago"
            
            print(f"Last build:        {last_build.strftime('%Y-%m-%d %H:%M:%S')} ({time_str})")
        except ValueError:
            print(f"Last build:        {stats['last_build']}")
    else:
        print(f"Last build:        Never")
    
    if stats['last_full_build']:
        try:
            last_full = datetime.fromisoformat(stats['last_full_build'])
            print(f"Last full build:   {last_full.strftime('%Y-%m-%d %H:%M:%S')}")
        except ValueError:
            print(f"Last full build:   {stats['last_full_build']}")
    else:
        print(f"Last full build:   Never")
    
    print("=" * 60)

def print_usage():
    """Print usage information"""
    print("Build Cache Management Tool")
    print()
    print("Usage:")
    print("  python manage_build_cache.py stats       - Show cache statistics")
    print("  python manage_build_cache.py clear       - Clear cache (force full rebuild)")
    print("  python manage_build_cache.py inspect     - Show detailed cache contents")
    print("  python manage_build_cache.py help        - Show this help message")
    print()
    print("Examples:")
    print("  python manage_build_cache.py stats")
    print("  python manage_build_cache.py clear")

def inspect_cache(builder):
    """Show detailed cache contents"""
    print("🔍 Detailed Cache Contents")
    print("=" * 60)
    
    # Show recent posts
    posts = builder.cache['posts']
    if posts:
        print(f"\n📝 Recent Posts ({len(posts)} total):")
        sorted_posts = sorted(
            posts.items(),
            key=lambda x: x[1].get('processed', ''),
            reverse=True
        )[:10]
        
        for url, data in sorted_posts:
            processed = data.get('processed', 'Unknown')
            try:
                proc_dt = datetime.fromisoformat(processed)
                proc_str = proc_dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                proc_str = processed
            
            print(f"  • {url}")
            print(f"    Processed: {proc_str}")
            print(f"    Hash: {data.get('hash', 'N/A')[:12]}...")
    else:
        print("\n📝 Posts: None cached")
    
    # Show recent pages
    pages = builder.cache['pages']
    if pages:
        print(f"\n📄 Recent Pages ({len(pages)} total):")
        sorted_pages = sorted(
            pages.items(),
            key=lambda x: x[1].get('processed', ''),
            reverse=True
        )[:10]
        
        for url, data in sorted_pages:
            processed = data.get('processed', 'Unknown')
            try:
                proc_dt = datetime.fromisoformat(processed)
                proc_str = proc_dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
                proc_str = processed
            
            print(f"  • {url}")
            print(f"    Processed: {proc_str}")
    else:
        print("\n📄 Pages: None cached")
    
    print("\n" + "=" * 60)

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command in ['help', '-h', '--help']:
        print_usage()
        sys.exit(0)
    
    # Initialize builder
    builder = IncrementalBuilder()
    
    if command == 'stats':
        print_stats(builder)
    
    elif command == 'clear':
        print("⚠️  This will clear the build cache and force a full rebuild next time.")
        response = input("Are you sure? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            builder.clear_cache()
            print("✅ Cache cleared successfully")
        else:
            print("❌ Operation cancelled")
    
    elif command == 'inspect':
        inspect_cache(builder)
    
    else:
        print(f"❌ Unknown command: {command}")
        print()
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
