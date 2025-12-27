#!/usr/bin/env python3
"""
WordPress Spell Check and Fix
Two-stage spell checking:
1. Fast traditional spell checker (pyspellchecker) for initial scan
2. Ollama AI for ambiguous cases with full context
"""

import os
import sys
import json
import argparse
import requests
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
from spellchecker import SpellChecker

class WordPressSpellCheckFixer:
    def __init__(self, ollama_url: str, wp_url: str, auth_token: str, model: str = "llama3.1:8b", ollama_auth: str = None):
        self.ollama_url = ollama_url.rstrip('/')
        self.wp_url = wp_url.rstrip('/')
        self.auth_token = auth_token
        self.model = model
        self.ollama_auth = ollama_auth
        self.ollama_checked = False
        
        # Session for WordPress API
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Basic {auth_token}',
            'User-Agent': 'SpellCheckerFixer/1.0'
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
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is reachable and list available models"""
        if self.ollama_checked:
            return True
        
        try:
            ollama_auth_tuple = None
            if self.ollama_auth and ':' in self.ollama_auth:
                username, password = self.ollama_auth.split(':', 1)
                ollama_auth_tuple = (username, password)
            
            # Try to list models
            print(f"🔍 Checking Ollama connection at {self.ollama_url}")
            response = requests.get(
                f'{self.ollama_url}/api/tags',
                auth=ollama_auth_tuple,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                models = result.get('models', [])
                print(f"✅ Ollama connected. Available models:")
                for model in models:
                    model_name = model.get('name', 'unknown')
                    print(f"   - {model_name}")
                    if self.model in model_name or model_name in self.model:
                        print(f"   ✅ Model '{self.model}' is available")
                
                self.ollama_checked = True
                return True
            else:
                print(f"⚠️  Ollama API returned {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not connect to Ollama: {str(e)}")
            return False
    
    def fast_spell_check(self, text: str) -> Set[str]:
        """
        First-pass spell check using traditional spell checker.
        Returns set of potentially misspelled words.
        """
        # Extract words (alphanumeric only, preserve case)
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
            return {'has_errors': False, 'corrections': []}
        
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
  "corrections": [
    {{
      "original": "teh",
      "corrected": "the"
    }}
  ]
}}

If no actual errors, return: {{"has_errors": false, "corrections": []}}
"""
        
        try:
            ollama_auth_tuple = None
            if self.ollama_auth and ':' in self.ollama_auth:
                username, password = self.ollama_auth.split(':', 1)
                ollama_auth_tuple = (username, password)
            
            api_endpoint = f'{self.ollama_url}/api/generate'
            print(f"      🔌 Calling Ollama API: {api_endpoint}")
            print(f"      📦 Model: {self.model}")
            
            response = requests.post(
                api_endpoint,
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'format': 'json',  # Force JSON output
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'num_predict': 1000
                    }
                },
                auth=ollama_auth_tuple,
                timeout=90  # Increased for batched content
            )
            
            print(f"      📡 Response status: {response.status_code}")
            
            # Handle 404 - model might not exist or wrong format
            if response.status_code == 404:
                print(f"⚠️  404 Error - Model '{self.model}' not found")
                print(f"   This usually means:")
                print(f"   1. The model name format is incorrect")
                print(f"   2. The model hasn't been pulled on the Ollama server")
                print(f"   3. Try 'llama3.1' instead of 'llama3.1:8b' or vice versa")
                
                # Try alternative model name format
                alternative_model = None
                if ':' in self.model:
                    alternative_model = self.model.split(':')[0]  # Try without tag
                else:
                    alternative_model = f"{self.model}:latest"  # Try with tag
                
                print(f"   🔄 Retrying with alternative model name: {alternative_model}")
                
                alt_response = requests.post(
                    api_endpoint,
                    json={
                        'model': alternative_model,
                        'prompt': prompt,
                        'format': 'json',  # Force JSON output
                        'stream': False,
                        'options': {
                            'temperature': 0.1,
                            'num_predict': 1000
                        }
                    },
                    auth=ollama_auth_tuple,
                    timeout=90  # Increased for batched content
                )
                
                if alt_response.status_code == 200:
                    print(f"   ✅ Success with {alternative_model}")
                    response = alt_response
                else:
                    print(f"   ❌ Alternative also failed: {alt_response.status_code}")
                    return {'has_errors': False, 'corrections': []}
            
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
                
                return {'has_errors': False, 'corrections': []}
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                print(f"   URL: {api_endpoint}")
                print(f"   Model: {self.model}")
                try:
                    error_body = response.text[:500]
                    print(f"   Response: {error_body}")
                except:
                    pass
                return {'has_errors': False, 'corrections': []}
                
        except Exception as e:
            print(f"⚠️  Ollama error: {str(e)}")
            return {'has_errors': False, 'corrections': []}
    
    def extract_text_sections(self, post: Dict) -> List[tuple]:
        """Extract text sections from a WordPress post"""
        sections = []
        
        # Title
        title = post.get('title', {}).get('rendered', '')
        if title:
            from html import unescape
            clean_title = BeautifulSoup(unescape(title), 'html.parser').get_text()
            sections.append(('title', clean_title))
        
        # Excerpt
        excerpt = post.get('excerpt', {}).get('rendered', '')
        if excerpt:
            from html import unescape
            excerpt_soup = BeautifulSoup(unescape(excerpt), 'html.parser')
            excerpt_text = excerpt_soup.get_text().strip()
            if excerpt_text:
                sections.append(('excerpt', excerpt_text))
        
        # Content
        content = post.get('content', {}).get('rendered', '')
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove code blocks and scripts
            for code in soup.find_all(['pre', 'code', 'script', 'style']):
                code.decompose()
            
            # Get paragraphs
            for i, p in enumerate(soup.find_all('p')):
                p_text = p.get_text().strip()
                if p_text and len(p_text) > 20:
                    sections.append((f'paragraph_{i+1}', p_text))
        
        return sections
    
    def check_post(self, post_id: int) -> Optional[Dict]:
        """
        Check a post and return corrections needed.
        Uses two-stage approach: fast traditional check, then Ollama for validation.
        """
        print(f"📄 Checking post ID: {post_id}")
        
        try:
            # Fetch with context=view to get published content only (not drafts/revisions)
            response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts/{post_id}',
                params={'context': 'view'}  # 'view' = published content only
            )
            
            if response.status_code != 200:
                print(f"   ❌ Failed to fetch: {response.status_code}")
                return None
            
            post = response.json()
            post_title = post.get('title', {}).get('rendered', 'Untitled')
            post_link = post.get('link', '')
            
            print(f"   Title: {post_title}")
            
            sections = self.extract_text_sections(post)
            
            # Stage 1: Fast traditional spell check on all sections
            print(f"   ⚡ Stage 1: Fast spell check...")
            all_candidate_errors = set()
            section_texts = {}
            
            for section_type, text in sections:
                if len(text.split()) < 5:
                    continue
                section_texts[section_type] = text
                candidates = self.fast_spell_check(text)
                all_candidate_errors.update(candidates)
            
            if not all_candidate_errors:
                print(f"   ✅ No potential errors found")
                return None
            
            print(f"   🔍 Stage 2: Validating {len(all_candidate_errors)} candidates with Ollama...")
            
            # Stage 2: Batch validate with Ollama using full context
            # Combine all text for context
            full_text = f"Title: {post_title}\n\n"
            for section_type, text in section_texts.items():
                full_text += f"{text}\n\n"
            
            result = self.check_with_ollama_batched(full_text, all_candidate_errors)
            
            all_corrections = []
            if result.get('has_errors'):
                corrections = result.get('corrections', [])
                for correction in corrections:
                    if not correction.get('original') or not correction.get('corrected'):
                        continue
                    
                    # Try to identify which section contains this error
                    error_word = correction['original']
                    section_found = 'unknown'
                    section_text = ''
                    for section_type, text in section_texts.items():
                        if error_word in text or error_word.lower() in text.lower():
                            section_found = section_type
                            section_text = text
                            break
                    
                    correction['section'] = section_found
                    correction['section_text'] = section_text
                    all_corrections.append(correction)
                    print(f"      ⚠️  {correction['original']} → {correction['corrected']} (in {section_found})")
            
            if all_corrections:
                print(f"   ⚠️  Found {len(all_corrections)} confirmed errors")
                return {
                    'post_id': post_id,
                    'title': post_title,
                    'link': post_link,
                    'corrections': all_corrections
                    # Note: Don't store post_data - we fetch fresh with context=edit when applying
                }
            else:
                print(f"   ✅ All candidates were false positives")
            
            return None
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None
    
    def check_recent_posts(self, count: int = 5, since: str = None) -> List[Dict]:
        """Check recent posts and return those needing corrections"""
        print(f"🔍 Checking posts...")
        
        # Check Ollama connection first
        if not self.check_ollama_connection():
            print("❌ Cannot connect to Ollama. Aborting.")
            return []
        
        print()
        
        try:
            params = {
                'per_page': count,
                'status': 'publish',
                'orderby': 'modified',
                'order': 'desc'
            }
            
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
                print("✅ No posts to check")
                return []
            
            print(f"📝 Found {len(posts)} post(s)")
            
            results = []
            for post in posts:
                result = self.check_post(post.get('id'))
                if result:
                    results.append(result)
                print()
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def apply_corrections_to_text(self, text: str, corrections: List[Dict]) -> str:
        """Apply corrections to text"""
        corrected_text = text
        
        for correction in corrections:
            original = correction['original']
            corrected = correction['corrected']
            
            # Replace all instances (case-sensitive first, then case-insensitive)
            corrected_text = corrected_text.replace(original, corrected)
            
            # Handle capitalized versions
            if original[0].islower() and corrected[0].islower():
                corrected_text = corrected_text.replace(
                    original.capitalize(),
                    corrected.capitalize()
                )
        
        return corrected_text
    
    def apply_corrections_to_post(self, post_corrections: Dict) -> bool:
        """Apply corrections to a WordPress post"""
        post_id = post_corrections['post_id']
        corrections = post_corrections['corrections']
        
        print(f"🔧 Applying corrections to post {post_id}: {post_corrections['title']}")
        
        # Fetch the post again with context=edit to get raw editable content
        try:
            response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts/{post_id}',
                params={'context': 'edit'}
            )
            
            if response.status_code != 200:
                print(f"   ❌ Failed to fetch post for editing: {response.status_code}")
                return False
            
            post_data = response.json()
        except Exception as e:
            print(f"   ❌ Error fetching post: {str(e)}")
            return False
        
        # Group corrections by section
        section_corrections = {}
        for correction in corrections:
            section = correction['section']
            if section not in section_corrections:
                section_corrections[section] = []
            section_corrections[section].append(correction)
        
        # Apply corrections to each section
        updated_data = {}
        
        # Title
        if 'title' in section_corrections:
            # Try to get raw content, fallback to rendered
            title_data = post_data.get('title', {})
            original_title = title_data.get('raw') or title_data.get('rendered', '')
            if not original_title:
                print(f"   ⚠️  Could not get title content")
            else:
                corrected_title = self.apply_corrections_to_text(
                    original_title,
                    section_corrections['title']
                )
                updated_data['title'] = corrected_title
                print(f"   Title: {original_title} → {corrected_title}")
        
        # Excerpt
        if 'excerpt' in section_corrections:
            excerpt_data = post_data.get('excerpt', {})
            original_excerpt = excerpt_data.get('raw') or excerpt_data.get('rendered', '')
            if original_excerpt:
                corrected_excerpt = self.apply_corrections_to_text(
                    original_excerpt,
                    section_corrections['excerpt']
                )
                updated_data['excerpt'] = corrected_excerpt
                print(f"   Excerpt corrected")
        
        # Content (paragraphs)
        content_corrections = [c for c in corrections if c['section'].startswith('paragraph_')]
        if content_corrections:
            content_data = post_data.get('content', {})
            original_content = content_data.get('raw') or content_data.get('rendered', '')
            if not original_content:
                print(f"   ⚠️  Could not get content")
                return False
            corrected_content = self.apply_corrections_to_text(
                original_content,
                content_corrections
            )
            updated_data['content'] = corrected_content
            print(f"   Content: {len(content_corrections)} correction(s) applied")
        
        # Update the post
        try:
            response = self.session.post(
                f'{self.wp_url}/wp-json/wp/v2/posts/{post_id}',
                json=updated_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Post updated successfully")
                return True
            else:
                print(f"   ❌ Failed to update: {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error updating post: {str(e)}")
            return False
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate markdown report of corrections"""
        report = ["# WordPress Spelling Corrections Report\n"]
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"Posts with corrections needed: {len(results)}\n")
        
        for result in results:
            report.append(f"## {result['title']}")
            report.append(f"**Post ID:** {result['post_id']}")
            report.append(f"**URL:** {result['link']}\n")
            
            # Group by section
            by_section = {}
            for correction in result['corrections']:
                section = correction['section']
                if section not in by_section:
                    by_section[section] = []
                by_section[section].append(correction)
            
            for section, corrections in by_section.items():
                report.append(f"### Section: {section}\n")
                for correction in corrections:
                    report.append(f"- **{correction['original']}** → **{correction['corrected']}**")
                    if correction.get('context'):
                        report.append(f"  - Context: _{correction['context']}_")
                    report.append("")
            
            report.append("---\n")
        
        return '\n'.join(report)

def main():
    parser = argparse.ArgumentParser(description='WordPress Spell Check and Fix')
    parser.add_argument('--check-only', action='store_true', 
                        help='Only check for errors, do not apply corrections')
    parser.add_argument('--count', type=int, default=5,
                        help='Number of posts to check')
    parser.add_argument('--apply-from-file', type=str,
                        help='Apply corrections from a JSON file')
    
    args = parser.parse_args()
    
    # Configuration
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'https://ollama.jameskilby.cloud')
    WP_URL = os.getenv('WP_URL', 'https://wordpress.jameskilby.cloud')
    AUTH_TOKEN = os.getenv('WP_AUTH_TOKEN')
    MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    OLLAMA_AUTH = os.getenv('OLLAMA_API_CREDENTIALS')
    SINCE_TIMESTAMP = os.getenv('SINCE_TIMESTAMP')
    
    if not AUTH_TOKEN:
        print('❌ Error: WP_AUTH_TOKEN environment variable is required')
        sys.exit(1)
    
    checker = WordPressSpellCheckFixer(
        ollama_url=OLLAMA_URL,
        wp_url=WP_URL,
        auth_token=AUTH_TOKEN,
        model=MODEL,
        ollama_auth=OLLAMA_AUTH
    )
    
    if args.apply_from_file:
        # Apply corrections from file
        print(f"📂 Loading corrections from {args.apply_from_file}")
        
        try:
            with open(args.apply_from_file, 'r') as f:
                results = json.load(f)
            
            print(f"Found {len(results)} post(s) with corrections")
            
            success_count = 0
            for result in results:
                if checker.apply_corrections_to_post(result):
                    success_count += 1
            
            print(f"\n✅ Applied corrections to {success_count}/{len(results)} posts")
            sys.exit(0 if success_count == len(results) else 1)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    
    else:
        # Check posts
        results = checker.check_recent_posts(
            count=args.count,
            since=SINCE_TIMESTAMP
        )
        
        if not results:
            print("\n✅ No corrections needed!")
            sys.exit(0)
        
        # Generate report
        report = checker.generate_report(results)
        
        # Save report
        report_file = Path('spelling_corrections_report.md')
        report_file.write_text(report)
        print(f"📊 Report saved to: {report_file}")
        
        # Save corrections as JSON for later application
        corrections_file = Path('spelling_corrections.json')
        with open(corrections_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Corrections saved to: {corrections_file}")
        
        if args.check_only:
            print("\n⚠️  Check-only mode: corrections not applied")
            print("Review the report and approve to apply corrections")
            sys.exit(1)  # Exit with error code to indicate corrections needed
        else:
            # Apply corrections immediately
            print("\n🔧 Applying corrections...")
            success_count = 0
            for result in results:
                if checker.apply_corrections_to_post(result):
                    success_count += 1
            
            print(f"\n✅ Applied corrections to {success_count}/{len(results)} posts")
            sys.exit(0 if success_count == len(results) else 1)

if __name__ == "__main__":
    main()
