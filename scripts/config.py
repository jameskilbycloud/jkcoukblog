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
    
    @classmethod
    def get_plausible_script_url(cls):
        """Get the full Plausible Analytics script URL"""
        return f"https://{cls.PLAUSIBLE_URL}/js/script.js"
    
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
