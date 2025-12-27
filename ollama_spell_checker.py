#!/usr/bin/env python3
"""
Ollama Spell Checker for WordPress Content
Two-stage spell checking:
1. Fast traditional spell checker (pyspellchecker) for initial scan
2. Ollama AI for ambiguous cases with full context
"""

import os
import sys
import requests
import json
import re
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Tuple, Set
from spellchecker import SpellChecker

class OllamaSpellChecker:
    def __init__(self, ollama_url: str, wp_url: str, auth_token: str, model: str = "llama3.1:8b", ollama_auth: str = None):
        self.ollama_url = ollama_url.rstrip('/')
        self.wp_url = wp_url.rstrip('/')
        self.auth_token = auth_token
        self.model = model
        self.ollama_auth = ollama_auth
        
        # Session for WordPress API
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Basic {auth_token}',
            'User-Agent': 'SpellChecker/1.0'
        })
        
        # Initialize traditional spell checker
        self.spell = SpellChecker()
        
        # Common technical terms that shouldn't be flagged
        self.whitelist = {
            'vmware', 'vsphere', 'vsan', 'vmc', 'kubernetes', 'homelab',
            'cloudflare', 'github', 'ansible', 'terraform', 'docker',
            'postgres', 'nginx', 'linux', 'ubuntu', 'api', 'json',
            'yaml', 'cli', 'devops', 'cicd', 'nvme', 'pcie', 'gb', 'tb',
            'cpu', 'gpu', 'ram', 'ssd', 'nas', 'iscsi', 'nfs', 'vlan',
            'inteligent',  # Historical misspelling in redirects
            'acast', 'plausible', 'indexnow', 'netlify', 'vimeo',
            'srcset', 'iframe', 'jpegoptim', 'optipng', 'fuse'
        }
        
        # Add whitelist to spell checker's dictionary
        self.spell.word_frequency.load_words(self.whitelist)
    
    def fast_spell_check(self, text: str) -> Set[str]:
        """
        First-pass spell check using traditional spell checker.
        Returns set of potentially misspelled words.
        """
        # Extract words (alphanumeric only, preserve case for later)
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Check for misspellings (case-insensitive)
        misspelled = set()
        for word in words:
            word_lower = word.lower()
            # Skip very short words (likely abbreviations)
            if len(word_lower) < 3:
                continue
            # Skip whitelisted terms
            if word_lower in self.whitelist:
                continue
            # Check if misspelled
            if word_lower not in self.spell:
                misspelled.add(word)
        
        return misspelled
    
    def check_with_ollama_batched(self, full_text: str, candidate_errors: Set[str]) -> Dict:
        """
        Use Ollama to validate potential errors with full context.
        Batches all text sections together for efficiency.
        """
        if not candidate_errors:
            return {'has_errors': False, 'errors': []}
        
        candidates_list = ', '.join(sorted(candidate_errors))
        
        prompt = f"""You are a spell checker for technical blog content about DevOps, VMware, and cloud infrastructure.

Potential misspellings found: {candidates_list}

Review the full text below and determine which of these words are ACTUAL errors:
- Ignore proper nouns, technical terms, brand names, abbreviations
- Ignore intentional informal language
- Only flag clear spelling mistakes

Full text:
\"\"\"
{full_text}
\"\"\"

Respond ONLY with valid JSON:
{{
  "has_errors": true/false,
  "errors": [
    {{
      "word": "teh",
      "suggestion": "the",
      "type": "spelling"
    }}
  ]
}}

If no actual errors, return: {{"has_errors": false, "errors": []}}
"""
        
        try:
            # Prepare authentication for Ollama if provided
            ollama_auth_tuple = None
            if self.ollama_auth:
                # Parse username:password format
                if ':' in self.ollama_auth:
                    username, password = self.ollama_auth.split(':', 1)
                    ollama_auth_tuple = (username, password)
            
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'format': 'json',  # Force JSON output for better reliability
                    'stream': False,
                    'options': {
                        'temperature': 0.1,  # Low temperature for consistent results
                        'num_predict': 1000
                    }
                },
                auth=ollama_auth_tuple,
                timeout=90  # Increased timeout for batched content
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Try to parse as JSON directly first
                try:
                    parsed = json.loads(response_text)
                    return parsed
                except json.JSONDecodeError:
                    # Fallback: Extract JSON from response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group())
                            return parsed
                        except json.JSONDecodeError:
                            pass
                
                return {'has_errors': False, 'errors': []}
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return {'has_errors': False, 'errors': []}
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Ollama connection error: {str(e)}")
            return {'has_errors': False, 'errors': []}
        except Exception as e:
            print(f"⚠️  Unexpected error: {str(e)}")
            return {'has_errors': False, 'errors': []}
    
    def extract_text_from_html(self, html_content: str, post_title: str = '', post_excerpt: str = '') -> List[Tuple[str, str]]:
        """
        Extract text content from HTML for spell checking
        Returns list of (text_type, content) tuples
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        texts = []
        
        # Add title if provided (from API)
        if post_title:
            # Decode HTML entities like &#8211;
            from html import unescape
            clean_title = unescape(post_title)
            texts.append(('title', clean_title))
        
        # Add excerpt if provided (from API)
        if post_excerpt:
            from html import unescape
            clean_excerpt = unescape(post_excerpt)
            # Strip HTML tags from excerpt
            excerpt_soup = BeautifulSoup(clean_excerpt, 'html.parser')
            excerpt_text = excerpt_soup.get_text().strip()
            if excerpt_text:
                texts.append(('excerpt', excerpt_text))
        
        # Remove code blocks, scripts, and styles before processing
        for code in soup.find_all(['pre', 'code', 'script', 'style']):
            code.decompose()
        
        # Get all paragraphs (REST API content is just the post content HTML)
        for i, p in enumerate(soup.find_all('p')):
            p_text = p.get_text().strip()
            if p_text and len(p_text) > 20:  # Skip very short paragraphs
                texts.append((f'paragraph_{i+1}', p_text))
        
        # Get headings
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4'])):
            heading_text = heading.get_text().strip()
            if heading_text and len(heading_text) > 5:
                texts.append((f'heading_{i+1}', heading_text))
        
        return texts
    
    def check_post(self, post_id: int) -> Dict:
        """
        Check a single WordPress post for spelling errors.
        Uses two-stage approach: fast traditional check, then Ollama for validation.
        """
        print(f"📄 Checking post ID: {post_id}")
        
        try:
            # Fetch post from WordPress API
            response = self.session.get(f'{self.wp_url}/wp-json/wp/v2/posts/{post_id}')
            
            if response.status_code != 200:
                return {'error': f'Failed to fetch post: {response.status_code}'}
            
            post = response.json()
            post_title = post.get('title', {}).get('rendered', 'Untitled')
            post_link = post.get('link', '')
            post_excerpt = post.get('excerpt', {}).get('rendered', '')
            
            print(f"   Title: {post_title}")
            print(f"   URL: {post_link}")
            
            # Get the rendered HTML content
            html_content = post.get('content', {}).get('rendered', '')
            if not html_content:
                return {'error': 'No content found'}
            
            # Extract text sections (pass title and excerpt from API)
            texts = self.extract_text_from_html(html_content, post_title, post_excerpt)
            print(f"   Found {len(texts)} text sections")
            
            # Stage 1: Fast traditional spell check on all sections
            print(f"   ⚡ Stage 1: Fast spell check...")
            all_candidate_errors = set()
            section_texts = {}
            
            for section_type, text in texts:
                if len(text.split()) < 5:
                    continue
                section_texts[section_type] = text
                candidates = self.fast_spell_check(text)
                all_candidate_errors.update(candidates)
            
            if not all_candidate_errors:
                print(f"   ✅ No potential errors found")
                return {
                    'post_id': post_id,
                    'title': post_title,
                    'link': post_link,
                    'errors': [],
                    'has_errors': False
                }
            
            print(f"   🔍 Stage 2: Validating {len(all_candidate_errors)} candidates with Ollama...")
            
            # Stage 2: Batch validate with Ollama using full context
            # Combine all text for context
            full_text = f"Title: {post_title}\n\n"
            if post_excerpt:
                from html import unescape
                clean_excerpt = unescape(post_excerpt)
                excerpt_soup = BeautifulSoup(clean_excerpt, 'html.parser')
                excerpt_text = excerpt_soup.get_text().strip()
                if excerpt_text:
                    full_text += f"Excerpt: {excerpt_text}\n\n"
            
            for section_type, text in section_texts.items():
                full_text += f"{text}\n\n"
            
            result = self.check_with_ollama_batched(full_text, all_candidate_errors)
            
            all_errors = []
            if result.get('has_errors'):
                errors_found = result.get('errors', [])
                for error in errors_found:
                    # Skip malformed errors
                    if not error.get('word'):
                        continue
                    
                    # Try to identify which section contains this error
                    error_word = error['word']
                    section_found = 'unknown'
                    for section_type, text in section_texts.items():
                        if error_word in text or error_word.lower() in text.lower():
                            section_found = section_type
                            break
                    
                    error['section'] = section_found
                    error['type'] = error.get('type', 'spelling')
                    all_errors.append(error)
                    print(f"      ⚠️  {error['type']}: {error['word']} → {error.get('suggestion', '?')} (in {section_found})")
            
            if all_errors:
                print(f"   ⚠️  Found {len(all_errors)} confirmed errors")
            else:
                print(f"   ✅ All candidates were false positives")
            
            return {
                'post_id': post_id,
                'title': post_title,
                'link': post_link,
                'errors': all_errors,
                'has_errors': len(all_errors) > 0
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_recent_posts(self, count: int = 5, since: str = None) -> List[Dict]:
        """
        Check recent WordPress posts for spelling errors
        Args:
            count: Maximum number of posts to check
            since: ISO 8601 timestamp - only check posts modified after this time
        """
        if since:
            print(f"🔍 Checking posts modified since {since}...")
        else:
            print(f"🔍 Checking {count} most recent posts...")
        
        try:
            params = {
                'per_page': count,
                'status': 'publish',
                'orderby': 'modified',
                'order': 'desc'
            }
            
            # Add modified_after filter if timestamp provided
            if since:
                params['modified_after'] = since
            
            response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params=params
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch posts: {response.status_code}")
                return []
            
            posts = response.json()
            
            if not posts:
                print("✅ No posts modified since last check")
                return []
            
            print(f"📝 Found {len(posts)} post(s) to check")
            results = []
            
            for post in posts:
                post_id = post.get('id')
                result = self.check_post(post_id)
                results.append(result)
                print()
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def generate_report(self, results: List[Dict]) -> str:
        """
        Generate a markdown report of spelling errors
        """
        report = ["# Spelling and Grammar Check Report\n"]
        report.append(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        posts_with_errors = [r for r in results if r.get('has_errors')]
        posts_clean = [r for r in results if not r.get('has_errors') and 'error' not in r]
        
        report.append(f"## Summary\n")
        report.append(f"- Total posts checked: {len(results)}")
        report.append(f"- Posts with errors: {len(posts_with_errors)}")
        report.append(f"- Posts clean: {len(posts_clean)}\n")
        
        if posts_with_errors:
            report.append("## Posts with Errors\n")
            
            for result in posts_with_errors:
                report.append(f"### {result['title']}")
                report.append(f"**URL**: {result['link']}\n")
                
                for error in result['errors']:
                    # Skip errors missing required keys (shouldn't happen but be defensive)
                    if not error.get('word') or not error.get('type'):
                        continue
                    
                    report.append(f"- **{error.get('type', 'ERROR').upper()}** in `{error.get('section', 'unknown')}`:")
                    report.append(f"  - Word: `{error['word']}`")
                    if error.get('suggestion'):
                        report.append(f"  - Suggestion: `{error['suggestion']}`")
                    if error.get('context'):
                        report.append(f"  - Context: _{error['context']}_")
                    report.append("")
        
        if posts_clean:
            report.append("## Posts with No Errors ✅\n")
            for result in posts_clean:
                report.append(f"- {result['title']}")
        
        return '\n'.join(report)

def main():
    """
    Main function to run spell checker
    """
    # Configuration
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'https://ollama.jameskilby.cloud')
    WP_URL = os.getenv('WP_URL', 'https://wordpress.jameskilby.cloud')
    AUTH_TOKEN = os.getenv('WP_AUTH_TOKEN')
    MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    OLLAMA_AUTH = os.getenv('OLLAMA_API_CREDENTIALS')  # Format: username:password
    
    if not AUTH_TOKEN:
        print('❌ Error: WP_AUTH_TOKEN environment variable is required')
        print('   Set it with: export WP_AUTH_TOKEN="your_token_here"')
        sys.exit(1)
    
    # Parse command line arguments
    post_count = 5
    since_timestamp = os.getenv('SINCE_TIMESTAMP')  # ISO 8601 format
    
    if len(sys.argv) > 1:
        try:
            post_count = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [number_of_posts]")
            sys.exit(1)
    
    print(f"🚀 Ollama Spell Checker")
    print(f"Ollama: {OLLAMA_URL}")
    print(f"WordPress: {WP_URL}")
    print(f"Model: {MODEL}")
    print("="*60)
    print()
    
    # Create checker
    checker = OllamaSpellChecker(
        ollama_url=OLLAMA_URL,
        wp_url=WP_URL,
        auth_token=AUTH_TOKEN,
        model=MODEL,
        ollama_auth=OLLAMA_AUTH
    )
    
    # Check posts
    results = checker.check_recent_posts(count=post_count, since=since_timestamp)
    
    # Generate report
    if results:
        report = checker.generate_report(results)
        
        # Save report
        report_file = Path('spelling_check_report.md')
        report_file.write_text(report)
        
        print("\n" + "=" * 60)
        print(f"📊 Report saved to: {report_file}")
        print()
        print(report)
        
        # Exit with error code if errors found
        if any(r.get('has_errors') for r in results):
            print("\n⚠️  Spelling errors found! Please review the report.")
            sys.exit(1)
        else:
            print("\n✅ No spelling errors found!")
            sys.exit(0)
    else:
        print("❌ No results to report")
        sys.exit(1)

if __name__ == "__main__":
    main()
