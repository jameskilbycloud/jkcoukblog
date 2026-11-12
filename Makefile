# WordPress to Static Site — Build Pipeline
# Usage: make build       (full pipeline)
#        make generate    (generate only)
#        make optimize    (optimize only)
#        make validate    (all validation)
#        make help        (show targets)

SHELL := /bin/bash
STATIC_DIR ?= ./static-output
# Optimise/validate/serve what `make generate` just wrote. CI builds in
# static-output too and only moves it to public/ at publish time; public/ is
# gitignored (the published site lives on the site branch — see fetch-site).
OUTPUT_DIR ?= $(STATIC_DIR)
WORKERS ?= 4

.PHONY: help build generate optimize validate validate-source test-csp \
        spell-check deploy-local clean install install-dev purge-kv-cache \
        purge-kv-cache-dry-run crux drift drift-snapshot fetch-site lint test \
        validate-content validate-html validate-deployment optimize-images \
        optimize-css optimize-html internal-links minify-js compress \
        indexnow changelog stats

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Full Pipeline ────────────────────────────────────────────────

build: validate-source generate optimize validate ## Full build pipeline (generate + optimize + validate)
	@echo ""
	@echo "✅ Full build complete!"

# ─── Installation ─────────────────────────────────────────────────

install: ## Install Python dependencies
	pip install -r requirements.txt

install-dev: ## Install all dependencies (including CI/dev tools)
	pip install -r requirements.txt -r requirements-dev.txt

# ─── Generation ───────────────────────────────────────────────────

generate: ## Generate static site from WordPress
	python3 scripts/wp_to_static_generator.py $(STATIC_DIR)
	python3 scripts/markdown_exporter.py $(STATIC_DIR) $(STATIC_DIR)/markdown https://jameskilby.co.uk
	python3 scripts/markdown_api.py $(STATIC_DIR)/markdown $(STATIC_DIR)/api
	python3 scripts/generate_llms_txt.py $(STATIC_DIR)/markdown $(STATIC_DIR) --with-full

# ─── Validation ───────────────────────────────────────────────────

validate-source: ## Validate WordPress source health
	python3 scripts/validate_wordpress_source.py

test-csp: ## Validate CSP headers for all third-party services
	python3 scripts/test_csp.py

validate-content: ## Run content quality checks (non-blocking)
	-python3 scripts/content_validator.py $(OUTPUT_DIR)

validate-html: ## Validate final HTML structure
	python3 scripts/validate_html.py $(OUTPUT_DIR)

validate-deployment: ## Post-optimisation deployment validation
	python3 scripts/validate_deployment.py $(OUTPUT_DIR)

validate: test-csp validate-html validate-deployment ## Run all validation checks

# ─── Lint + Unit Tests (mirrors .github/workflows/python-checks.yml) ──

lint: ## Ruff lint over scripts/ and tests/
	ruff check scripts/ tests/

test: ## Run the pytest unit test suite
	pytest tests/ -v

# ─── Optimisation ─────────────────────────────────────────────────

optimize-images: ## Encode AVIF/WebP (FORCE=1 re-encodes everything); <picture> markup is done by optimize-html
	python3 scripts/optimize_images.py $(OUTPUT_DIR) --workers $(WORKERS) --skip-html $(if $(FORCE),--force)

optimize-css: ## Optimise CSS files (remove unused + minify)
	python3 scripts/optimize_css.py $(OUTPUT_DIR)
	python3 scripts/optimize_css.py $(OUTPUT_DIR) --minify-only

optimize-html: ## Optimise HTML (single-pass: SEO + pictures + perf + critical CSS + minify)
	python3 scripts/html_transformer.py $(OUTPUT_DIR)

internal-links: ## Contextual internal links for orphan posts (post-transform, over final output)
	python3 scripts/internal_links.py $(OUTPUT_DIR)

minify-js: ## Minify JS (WP-Optimize minify is disabled; nothing else does this)
	python3 scripts/minify_js.py $(OUTPUT_DIR)

compress: ## Brotli + Gzip pre-compression
	python3 scripts/brotli_compress.py $(OUTPUT_DIR)

# internal-links runs AFTER optimize-html: it operates on the final, transformed
# output so its links can't be dropped by the incremental-skip / raw-snapshot /
# transform interactions that silently reverted the earlier in-generator pass.
# minify-js must precede compress so the .br/.gz sidecars are built from the
# minified bytes rather than the originals.
optimize: optimize-images optimize-css optimize-html internal-links minify-js compress ## Run all optimisation steps

# ─── Post-Deploy ──────────────────────────────────────────────────

indexnow: ## Submit changed URLs to IndexNow
	python3 scripts/submit_indexnow.py $(OUTPUT_DIR)

changelog: ## Generate changelog page
	python3 scripts/generate_changelog.py $(OUTPUT_DIR)

stats: ## Generate stats page (requires PLAUSIBLE_SHARE_LINK)
	python3 scripts/generate_stats_page.py $(OUTPUT_DIR)

# ─── SEO Monitoring ───────────────────────────────────────────────

crux: ## Fetch real Core Web Vitals field data from CrUX (requires CRUX_API_KEY)
	python3 scripts/fetch_crux_metrics.py --out docs/seo-audit-2026-06/crux-latest.json

drift: ## Check the built site for SEO drift against the committed baseline
	python3 scripts/drift_baseline.py --check $(OUTPUT_DIR)

drift-snapshot: ## Re-baseline SEO signals from the built site (commit the result)
	python3 scripts/drift_baseline.py --snapshot $(OUTPUT_DIR)

# ─── Spell Check ──────────────────────────────────────────────────

SPELL_POSTS ?= 3

spell-check: ## AI spell check the last SPELL_POSTS posts (requires WP_AUTH_TOKEN + OLLAMA_API_CREDENTIALS)
	python3 scripts/ollama_spell_checker.py $(SPELL_POSTS)

# ─── Local Development ───────────────────────────────────────────

fetch-site: ## Extract the published site (site branch) into ./public for inspection
	git fetch --depth=1 origin site
	rm -rf ./public
	git archive FETCH_HEAD public | tar -x
	@echo "✅ ./public = site@$$(git rev-parse --short FETCH_HEAD) — serve it with: make deploy-local OUTPUT_DIR=./public"

deploy-local: ## Start local preview server on port 8080
	@echo "Starting local server at http://localhost:8080"
	python3 -m http.server 8080 --directory $(OUTPUT_DIR)

# ─── Cleanup ──────────────────────────────────────────────────────

purge-kv-cache: ## Bulk-delete all html:* entries from HTML_CACHE KV (requires CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID)
	python3 scripts/purge_html_kv_cache.py

purge-kv-cache-dry-run: ## Preview what purge-kv-cache would delete (no changes)
	python3 scripts/purge_html_kv_cache.py --dry-run

clean: ## Remove temporary build artifacts
	rm -rf $(STATIC_DIR)
	rm -f validation-report.json indexnow-submission.json
	@echo "✅ Build artifacts cleaned"
