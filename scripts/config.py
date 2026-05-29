"""
Centralized configuration for WordPress to Static Site Generator

This configuration file centralizes all URLs and domains used throughout the project.
Secrets (tokens, credentials) remain in environment variables and GitHub Secrets.

Usage:
    from config import Config
    
    config = Config()
    print(config.WP_URL)
    print(config.TARGET_DOMAIN)
"""

import os


class Config:
    """Centralized configuration management for URLs and domains"""
    
    # WordPress Configuration
    WP_URL = 'https://wordpress.jameskilby.cloud'
    
    # Target Domains
    TARGET_DOMAIN = 'https://jameskilby.co.uk'
    STAGING_DOMAIN = 'jkcoukblog.pages.dev'
    
    # Service URLs
    OLLAMA_URL = 'https://ollama.jameskilby.cloud'
    OLLAMA_MODEL = 'llama3.1:8b'
    PLAUSIBLE_URL = 'plausible.jameskilby.cloud'
    
    # Processing Configuration
    MAX_WORKERS = 3
    REQUEST_TIMEOUT = 30

    # Homepage stats — feeds the terminal stats block on the homepage.
    # vExpert membership year used to compute years.vexpert; update if the
    # source-of-truth changes.
    VEXPERT_START_YEAR = 2015

    # Canonical homepage <title>. Applied at build time by
    # scripts/fix_seo_issues.py:fix_homepage_title so <title>, og:title,
    # and twitter:title stay in lockstep regardless of what Rank Math /
    # WordPress emits. Target ~50-60 chars so Google doesn't rewrite it
    # in SERPs (pixel budget ≈ 580px ≈ 55-60 chars).
    HOMEPAGE_TITLE = "James Kilby — VMware, Homelab & Cloud Infrastructure Notes"

    # Paths that should carry <meta name="robots" content="noindex,follow">
    # at serve time AND be excluded from sitemap.xml. "follow" preserves
    # link discovery so Google still crawls posts linked from these pages;
    # noindex stops the thin/utility pages themselves from competing in the
    # index and inflating crawl budget. Each entry is a regex matched against
    # the URL path (with trailing slash, e.g. "/category/aws/").
    #
    # See scripts/fix_seo_issues.py:fix_thin_archive_noindex (injects the
    # meta tag) and wp_to_static_generator.py:_should_exclude_from_sitemap
    # (drops them from sitemap). Both read this list — single source of truth.
    NOINDEX_PATH_PATTERNS = (
        r'^/category/.+',          # category archives (thin — list of post excerpts)
        r'^/tag/.+',               # tag archives (currently 404 but future-proof)
        r'^/page/\d+/?$',          # root pagination (no unique content)
        r'^/changelog/?$',          # auto-generated changelog
        r'^/evs/?$',               # raw event log (described as "non-content" in validate_seo)
        r'^/stats/?$',             # auto-generated stats page
        r'^/privacy-policy-2/?$',  # legal page — required, doesn't need to rank
    )
    
    @classmethod
    def get_plausible_script_url(cls):
        """Same-origin path served by the Cloudflare Worker, which proxies to
        the Plausible CE instance on PLAUSIBLE_URL. Same-origin so ad blockers
        don't match the third-party host and the script is edge-cached."""
        return "/js/script.js"
    
    @classmethod
    def get_plausible_domain(cls):
        """Get the domain name for Plausible Analytics tracking"""
        # Extract domain without protocol
        return cls.TARGET_DOMAIN.replace('https://', '').replace('http://', '').split('/')[0]
    
    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)"""
        print("=" * 60)
        print("Configuration")
        print("=" * 60)
        print(f"WordPress URL:        {cls.WP_URL}")
        print(f"Target Domain:        {cls.TARGET_DOMAIN}")
        print(f"Staging Domain:       {cls.STAGING_DOMAIN}")
        print(f"Ollama URL:           {cls.OLLAMA_URL}")
        print(f"Ollama Model:         {cls.OLLAMA_MODEL}")
        print(f"Plausible URL:        {cls.PLAUSIBLE_URL}")
        print(f"Max Workers:          {cls.MAX_WORKERS}")
        print(f"Request Timeout:      {cls.REQUEST_TIMEOUT}s")
        print("=" * 60)


# Create a singleton instance for easy imports
config = Config()


if __name__ == "__main__":
    # When run directly, print configuration
    Config.print_config()
    print("\n✅ Configuration loaded successfully!")
