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

    # X/Twitter handle for attribution meta tags. Applied at build time by
    # scripts/fix_seo_issues.py:fix_twitter_attribution to every page that
    # already emits a twitter:card. Both twitter:site (the site's handle)
    # and twitter:creator (the post author's handle) are set to this value
    # — single-author blog, no per-post variance.
    TWITTER_HANDLE = "@jameskilbynet"

    # ── Person / E-E-A-T schema enrichment ──────────────────────────────────
    # Applied at build time by scripts/fix_seo_issues.py:fix_person_enrichment
    # to every Person entity in JSON-LD whose name matches PERSON_CANONICAL_NAMES
    # below (i.e. the site owner — single-author blog, so one Person identity).
    # Google leans hard on E-E-A-T (Experience, Expertise, Authoritativeness,
    # Trustworthiness) for technical content. Connecting the author's @id to
    # their professional profiles via sameAs strengthens Google's entity graph
    # association and improves trust signal for every page.

    # Names treated as "the site owner" — Rank Math sometimes emits "James"
    # (the WordPress display name) and sometimes "James Kilby" (the schema
    # person name). Both refer to the same Person.
    PERSON_CANONICAL_NAMES = ('James Kilby', 'James')

    # Canonical social/professional profiles. Single source of truth for the
    # footer "Connect with me" links (wp_to_static_generator.add_social_links)
    # AND the JSON-LD sameAs graph below. name/color feed the rendered links.
    SOCIAL_PROFILES = (
        {'name': 'GitHub',   'url': 'https://github.com/jameskilbynet',         'color': '#333'},
        {'name': 'Twitter',  'url': 'https://x.com/jameskilbynet',              'color': '#1da1f2'},
        {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/in/james-kilby/', 'color': '#0077b5'},
    )

    # sameAs URLs — the canonical professional profile graph for entity linking.
    # Pre-existing JSON-LD links to wordpress.jameskilby.cloud (the private CMS),
    # which is wrong on a public schema; this list replaces that.
    #
    # The same list is applied to both Person AND Organization entities (by
    # fix_person_enrichment and fix_organization_sameas respectively) — this
    # is a single-author blog so Person.sameAs and Organization.sameAs should
    # describe the same identity graph.
    PERSON_SAME_AS = tuple(p['url'] for p in SOCIAL_PROFILES)

    # GitHub repo (owner/name) whose issues back Utterances comments. The
    # Utterances app must stay installed on this exact repo — do not change
    # this to the code repo without migrating the comment issues.
    UTTERANCES_REPO = 'jameskilbynet/jkcoukblog'

    # Site logo, used as the default og:image fallback and the Organization
    # JSON-LD logo. Path is relative to TARGET_DOMAIN.
    DEFAULT_OG_IMAGE_PATH = '/wp-content/uploads/2025/12/ChatGPT-Image-Dec-17-2025-at-09_03_10-PM.png'

    PERSON_JOB_TITLE = 'Cloud / Infrastructure Architect'

    # Topic-expertise array. Pulled from the actual category distribution
    # on the site — only areas with multiple substantive posts.
    PERSON_KNOWS_ABOUT = (
        'VMware vSphere',
        'VMware Cloud on AWS',
        'Homelab Infrastructure',
        'Cloudflare',
        'AWS',
        'Ansible',
        'Kubernetes',
        'Storage',
        'Self-hosted AI',
        'Network Automation',
    )

    # Professional awards — see the homepage tagline, vexpert category, and
    # VEXPERT_START_YEAR above. vExpert is a public VMware MVP-style program.
    PERSON_AWARDS = (
        'VMware vExpert',
    )

    # ── Topic → entity map for Article about/mentions enrichment ──────────────
    # Applied at build time by scripts/fix_seo_issues.py:fix_article_entity_links.
    # Each post's articleSection + keywords + headline are matched (whole-word,
    # case-insensitive) against the keys below; matches become schema.org
    # `about` (the primary topic) and `mentions` (all matched topics) entities
    # with `sameAs` pointing at the authoritative Wikipedia/Wikidata record.
    #
    # This connects free-text topics to recognised entities in Google's and AI
    # engines' knowledge graphs — the same E-E-A-T entity-reconciliation play as
    # PERSON_SAME_AS, but for the *subject matter* rather than the author.
    #
    # Conservative by design: only emit entities we have an explicit, verified
    # mapping for. Every sameAs URL below is a stable Wikipedia article (and a
    # Wikidata QID where confidently known); do NOT add an entry on a guess — a
    # wrong sameAs is worse than an absent one. Keys are lowercase match terms;
    # keep them aligned with PERSON_KNOWS_ABOUT and the real category taxonomy.
    TOPIC_ENTITIES = {
        'vmware':     {'name': 'VMware',
                       'sameAs': ('https://en.wikipedia.org/wiki/VMware',
                                  'https://www.wikidata.org/wiki/Q14958')},
        'vsphere':    {'name': 'VMware vSphere',
                       'sameAs': ('https://en.wikipedia.org/wiki/VSphere',)},
        'kubernetes': {'name': 'Kubernetes',
                       'sameAs': ('https://en.wikipedia.org/wiki/Kubernetes',)},
        'cloudflare': {'name': 'Cloudflare',
                       'sameAs': ('https://en.wikipedia.org/wiki/Cloudflare',)},
        'ansible':    {'name': 'Ansible',
                       'sameAs': ('https://en.wikipedia.org/wiki/Ansible_(software)',)},
        'docker':     {'name': 'Docker',
                       'sameAs': ('https://en.wikipedia.org/wiki/Docker_(software)',)},
        'aws':        {'name': 'Amazon Web Services',
                       'sameAs': ('https://en.wikipedia.org/wiki/Amazon_Web_Services',)},
        'proxmox':    {'name': 'Proxmox Virtual Environment',
                       'sameAs': ('https://en.wikipedia.org/wiki/Proxmox_Virtual_Environment',)},
        'terraform':  {'name': 'Terraform',
                       'sameAs': ('https://en.wikipedia.org/wiki/Terraform_(software)',)},
        'nvidia':     {'name': 'Nvidia',
                       'sameAs': ('https://en.wikipedia.org/wiki/Nvidia',)},
    }

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
