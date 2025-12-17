#!/usr/bin/env python3
"""Test script to verify publisher URL enhancement in JSON-LD"""

import json

# Sample JSON-LD data similar to what's on the site
sample_data = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": ["Person", "Organization"],
            "@id": "/#person",
            "name": "Jameskilbycouk"
        },
        {
            "@type": "WebSite",
            "@id": "/#website",
            "url": "https://jameskilby.co.uk",
            "publisher": {"@id": "/#person"},
            "inLanguage": "en-GB"
        },
        {
            "@type": "BlogPosting",
            "headline": "Test Article",
            "author": {"@id": "/author/admin/"},
            "publisher": {"@id": "/#person"},
            "description": "Test description",
            "wordCount": 1200,
            "timeRequired": "PT6M"
        }
    ]
}

target_domain = "https://jameskilby.co.uk"
modified = False

# Get items from @graph
items = sample_data.get('@graph', [sample_data]) if '@graph' in sample_data else [sample_data]

# First pass: Ensure Organization/Person publishers have URL
for item in items:
    if isinstance(item, dict):
        item_types = item.get('@type', [])
        # Handle both single type and array of types
        if not isinstance(item_types, list):
            item_types = [item_types]
        
        # If this is an Organization or Person that acts as publisher
        if any(t in ['Organization', 'Person'] for t in item_types):
            if '@id' in item and '/#person' in item['@id']:
                if 'url' not in item:
                    item['url'] = target_domain
                    modified = True
                    print(f"✅ Added URL to publisher entity: {target_domain}")

# Second pass: Process BlogPosting items
for item in items:
    if isinstance(item, dict) and item.get('@type') == 'BlogPosting':
        # Ensure publisher reference has URL (for inline publisher objects)
        if 'publisher' in item and isinstance(item['publisher'], dict):
            if '@id' not in item['publisher'] and 'url' not in item['publisher']:
                # Inline publisher without @id reference
                item['publisher']['url'] = target_domain
                modified = True
                print(f"✅ Added publisher URL to inline publisher: {target_domain}")

print("\n" + "="*60)
print("ENHANCED JSON-LD:")
print("="*60)
print(json.dumps(sample_data, indent=2, ensure_ascii=False))

# Find the Person/Organization to verify it has URL
for item in items:
    if isinstance(item, dict):
        item_types = item.get('@type', [])
        if not isinstance(item_types, list):
            item_types = [item_types]
        
        if any(t in ['Organization', 'Person'] for t in item_types):
            print("\n" + "="*60)
            print("PUBLISHER ENTITY:")
            print("="*60)
            print(json.dumps(item, indent=2, ensure_ascii=False))
            if 'url' in item:
                print(f"\n✅ Publisher has URL: {item['url']}")
            else:
                print("\n❌ Publisher missing URL")
