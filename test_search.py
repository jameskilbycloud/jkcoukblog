#!/usr/bin/env python3
"""
Test Search Functionality
Quick test script to generate search index and verify it works
"""

import os
import json
import subprocess
import time
from pathlib import Path

def test_search_generation():
    """Test the search index generation"""
    print("🧪 Testing Search Functionality")
    print("=" * 50)
    
    # Check if public directory exists
    public_dir = Path('./public')
    if not public_dir.exists():
        print("❌ Public directory not found. Run your static generation first.")
        return False
    
    # Generate search index using the standalone script
    print("1️⃣  Generating search index...")
    try:
        result = subprocess.run([
            'python3', 'generate_search_index.py', 
            'public', 
            '--output', 'search-index.json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Search index generation failed: {result.stderr}")
            return False
        
        print("✅ Search index generated successfully")
        print(result.stdout)
        
    except FileNotFoundError:
        print("❌ generate_search_index.py not found")
        return False
    
    # Verify search index files exist
    search_index_file = public_dir / 'search-index.json'
    search_index_min_file = public_dir / 'search-index.min.json'
    
    if not search_index_file.exists():
        print("❌ search-index.json not created")
        return False
    
    if not search_index_min_file.exists():
        print("❌ search-index.min.json not created")
        return False
    
    # Load and validate search index
    print("\n2️⃣  Validating search index...")
    try:
        with open(search_index_file, 'r', encoding='utf-8') as f:
            search_data = json.load(f)
        
        if not isinstance(search_data, list):
            print("❌ Search index is not a list")
            return False
        
        if len(search_data) == 0:
            print("❌ Search index is empty")
            return False
        
        print(f"✅ Search index contains {len(search_data)} entries")
        
        # Validate structure of first entry
        if search_data:
            first_entry = search_data[0]
            required_fields = ['title', 'url', 'description', 'content', 'categories', 'tags']
            missing_fields = [field for field in required_fields if field not in first_entry]
            
            if missing_fields:
                print(f"❌ Missing fields in search entry: {missing_fields}")
                return False
            
            print("✅ Search index structure is valid")
            
            # Show sample entry
            print(f"\n📄 Sample entry:")
            print(f"   Title: {first_entry['title']}")
            print(f"   URL: {first_entry['url']}")
            print(f"   Description: {first_entry['description'][:100]}...")
            print(f"   Categories: {first_entry['categories']}")
            print(f"   Tags: {first_entry['tags'][:3]}...")
    
    except Exception as e:
        print(f"❌ Error validating search index: {e}")
        return False
    
    # Check file sizes
    print(f"\n3️⃣  File sizes:")
    full_size = search_index_file.stat().st_size
    min_size = search_index_min_file.stat().st_size
    
    print(f"   📄 search-index.json: {full_size / 1024:.1f} KB")
    print(f"   📄 search-index.min.json: {min_size / 1024:.1f} KB")
    print(f"   💾 Compression ratio: {(1 - min_size/full_size) * 100:.1f}%")
    
    # Check if search.js exists
    search_js_file = public_dir / 'js' / 'search.js'
    if search_js_file.exists():
        print("✅ search.js file found")
    else:
        print("⚠️  search.js file not found - copy it to public/js/search.js")
    
    return True

def test_local_server():
    """Start a local server for testing"""
    print("\n4️⃣  Starting local test server...")
    public_dir = Path('./public')
    
    if not public_dir.exists():
        print("❌ Public directory not found")
        return
    
    try:
        print("🌐 Starting server at http://localhost:8000")
        print("   Open your browser and test the search functionality")
        print("   Press Ctrl+C to stop the server")
        
        # Start HTTP server
        subprocess.run([
            'python3', '-m', 'http.server', '8000', 
            '--directory', str(public_dir)
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

def simulate_search_test():
    """Simulate search functionality test"""
    print("\n5️⃣  Simulating search test...")
    
    search_index_file = Path('./public/search-index.min.json')
    if not search_index_file.exists():
        print("❌ Search index not found")
        return
    
    try:
        with open(search_index_file, 'r', encoding='utf-8') as f:
            search_data = json.load(f)
        
        # Test search terms
        test_terms = ['homelab', 'vmware', 'docker', 'artificial intelligence', 'networking']
        
        print(f"Testing search with {len(test_terms)} sample terms:")
        
        for term in test_terms:
            matches = []
            term_lower = term.lower()
            
            for entry in search_data:
                # Simple text matching (simulating Fuse.js behavior)
                searchable_text = ' '.join([
                    entry['title'].lower(),
                    entry['description'].lower(),
                    entry['content'].lower(),
                    ' '.join(entry['categories']).lower(),
                    ' '.join(entry['tags']).lower()
                ])
                
                if term_lower in searchable_text:
                    matches.append(entry)
            
            print(f"   🔍 '{term}': {len(matches)} results")
            if matches:
                print(f"      Top result: {matches[0]['title']}")
        
        print("✅ Search simulation complete")
        
    except Exception as e:
        print(f"❌ Search simulation failed: {e}")

def main():
    """Main test function"""
    # Test search generation
    if not test_search_generation():
        print("\n❌ Search generation test failed")
        return
    
    # Simulate search functionality
    simulate_search_test()
    
    print(f"\n🎉 All tests passed!")
    print(f"\n📋 Next steps:")
    print(f"1. Copy search.js to your public/js/ directory")
    print(f"2. Add search script to your HTML templates")
    print(f"3. Test locally with: python3 test_search.py --server")
    print(f"4. Deploy your updated static site")
    
    # Ask if user wants to start local server
    if '--server' in os.sys.argv:
        test_local_server()

if __name__ == '__main__':
    main()