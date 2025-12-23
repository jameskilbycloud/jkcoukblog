#!/usr/bin/env python3
"""
IndexNow Submission Script
Submits all pages to search engines via IndexNow protocol
https://www.indexnow.org/
"""

import os
import sys
import json
import requests
import hashlib
import uuid
from pathlib import Path
from datetime import datetime

class IndexNowSubmitter:
    """Submit URLs to search engines using IndexNow protocol"""
    
    # IndexNow endpoint (can be any participating search engine)
    INDEXNOW_ENDPOINTS = [
        'https://api.indexnow.org/indexnow',  # General endpoint
        'https://www.bing.com/indexnow',      # Bing
        'https://yandex.com/indexnow',         # Yandex
    ]
    
    def __init__(self, site_domain, output_dir, key_location=None):
        """
        Initialize IndexNow submitter
        
        Args:
            site_domain: Your site domain (e.g., https://jameskilby.co.uk)
            output_dir: Directory containing the static site
            key_location: Optional path to store/read the API key
        """
        self.site_domain = site_domain.rstrip('/')
        self.output_dir = Path(output_dir)
        self.key_location = Path(key_location) if key_location else self.output_dir.parent / '.indexnow_key'
        
        # Get or generate API key
        self.api_key = self._get_or_create_key()
    
    def _get_or_create_key(self):
        """Get existing IndexNow key or create a new one"""
        if self.key_location.exists():
            key = self.key_location.read_text().strip()
            print(f"📋 Using existing IndexNow key from {self.key_location}")
            return key
        else:
            # Generate a new UUID-based key
            key = str(uuid.uuid4())
            self.key_location.write_text(key)
            print(f"🔑 Generated new IndexNow key: {key}")
            print(f"   Saved to: {self.key_location}")
            return key
    
    def create_key_file(self):
        """
        Create the key verification file that must be hosted at the root of your site
        This file proves you own the domain
        """
        key_file = self.output_dir / f'{self.api_key}.txt'
        key_file.write_text(self.api_key)
        print(f"✅ Created key verification file: {key_file.name}")
        print(f"   This file must be accessible at: {self.site_domain}/{self.api_key}.txt")
        return key_file
    
    def collect_urls(self):
        """Collect all URLs from the static site"""
        urls = []
        
        # Find all HTML files
        for html_file in self.output_dir.rglob('*.html'):
            relative_path = html_file.relative_to(self.output_dir)
            
            # Convert file path to URL path
            if relative_path.name == 'index.html':
                if relative_path.parent == Path('.'):
                    url_path = '/'
                else:
                    url_path = f'/{relative_path.parent}/'
            else:
                url_path = f'/{relative_path.with_suffix("")}/'
            
            # Construct full URL
            full_url = f'{self.site_domain}{url_path}'
            urls.append(full_url)
        
        # Remove duplicates and sort
        urls = sorted(set(urls))
        print(f"📊 Collected {len(urls)} URLs to submit")
        return urls
    
    def submit_urls(self, urls, batch_size=10000):
        """
        Submit URLs to IndexNow
        
        Args:
            urls: List of URLs to submit
            batch_size: Maximum URLs per request (IndexNow limit is 10,000)
        
        Returns:
            Dict with submission results
        """
        if not urls:
            print("⚠️  No URLs to submit")
            return {'success': False, 'message': 'No URLs provided'}
        
        print(f"\n🚀 Submitting {len(urls)} URLs to IndexNow...")
        
        # Split into batches if needed
        batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
        
        results = {
            'total_urls': len(urls),
            'batches': len(batches),
            'successful_batches': 0,
            'failed_batches': 0,
            'responses': []
        }
        
        for batch_idx, batch in enumerate(batches, 1):
            print(f"\n📤 Submitting batch {batch_idx}/{len(batches)} ({len(batch)} URLs)...")
            
            # Prepare payload
            payload = {
                'host': self.site_domain.replace('https://', '').replace('http://', ''),
                'key': self.api_key,
                'urlList': batch
            }
            
            # Try each endpoint until one succeeds
            success = False
            for endpoint in self.INDEXNOW_ENDPOINTS:
                try:
                    response = requests.post(
                        endpoint,
                        json=payload,
                        headers={
                            'Content-Type': 'application/json; charset=utf-8',
                            'User-Agent': 'IndexNowSubmitter/1.0'
                        },
                        timeout=30
                    )
                    
                    result = {
                        'batch': batch_idx,
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'success': False
                    }
                    
                    # IndexNow returns 200 for success, 202 for accepted
                    if response.status_code in [200, 202]:
                        result['success'] = True
                        success = True
                        results['successful_batches'] += 1
                        print(f"   ✅ Success! Status {response.status_code} from {endpoint}")
                        print(f"      Submitted {len(batch)} URLs")
                    else:
                        result['message'] = response.text[:200] if response.text else 'No response body'
                        print(f"   ⚠️  Status {response.status_code} from {endpoint}")
                        if response.text:
                            print(f"      Response: {response.text[:200]}")
                    
                    results['responses'].append(result)
                    
                    # If successful, don't try other endpoints
                    if success:
                        break
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏱️  Timeout for {endpoint}")
                    results['responses'].append({
                        'batch': batch_idx,
                        'endpoint': endpoint,
                        'success': False,
                        'message': 'Timeout'
                    })
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ Error with {endpoint}: {str(e)[:100]}")
                    results['responses'].append({
                        'batch': batch_idx,
                        'endpoint': endpoint,
                        'success': False,
                        'message': str(e)[:200]
                    })
            
            if not success:
                results['failed_batches'] += 1
                print(f"   ❌ All endpoints failed for batch {batch_idx}")
        
        return results
    
    def save_submission_log(self, results, log_file='indexnow-submission.json'):
        """Save submission results to a log file"""
        log_path = self.output_dir.parent / log_file
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'site_domain': self.site_domain,
            'results': results
        }
        
        # Append to existing log or create new one
        if log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
                if not isinstance(log_data, list):
                    log_data = [log_data]
            except:
                log_data = []
        else:
            log_data = []
        
        log_data.append(log_entry)
        
        # Keep only last 30 submissions
        log_data = log_data[-30:]
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\n📝 Submission log saved to: {log_path}")
    
    def submit_all(self):
        """Complete IndexNow submission workflow"""
        print("=" * 60)
        print("🔔 IndexNow URL Submission")
        print("=" * 60)
        print(f"Site: {self.site_domain}")
        print(f"Output: {self.output_dir}")
        print(f"Key: {self.api_key[:8]}...{self.api_key[-4:]}")
        print("=" * 60)
        
        # Create key verification file
        self.create_key_file()
        
        # Collect URLs
        urls = self.collect_urls()
        
        if not urls:
            print("❌ No URLs found to submit")
            return False
        
        # Submit to IndexNow
        results = self.submit_urls(urls)
        
        # Save log
        self.save_submission_log(results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SUBMISSION SUMMARY")
        print("=" * 60)
        print(f"Total URLs: {results['total_urls']}")
        print(f"Batches: {results['batches']}")
        print(f"✅ Successful: {results['successful_batches']}")
        print(f"❌ Failed: {results['failed_batches']}")
        
        if results['successful_batches'] > 0:
            print("\n✅ IndexNow submission completed successfully!")
            print(f"   Search engines will be notified about {results['total_urls']} URLs")
            print(f"\n💡 Make sure {self.api_key}.txt is accessible at:")
            print(f"   {self.site_domain}/{self.api_key}.txt")
            return True
        else:
            print("\n❌ IndexNow submission failed!")
            print("   Please check the error messages above")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python submit_indexnow.py <output_directory>")
        print("Example: python submit_indexnow.py ./static-output")
        print("\nThis script will:")
        print("  1. Generate or use existing IndexNow API key")
        print("  2. Create key verification file")
        print("  3. Collect all URLs from the static site")
        print("  4. Submit URLs to search engines via IndexNow")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    
    # Configuration
    SITE_DOMAIN = 'https://jameskilby.co.uk'
    
    # Create submitter instance
    submitter = IndexNowSubmitter(
        site_domain=SITE_DOMAIN,
        output_dir=output_dir
    )
    
    # Submit all URLs
    success = submitter.submit_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
