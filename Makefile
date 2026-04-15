# WordPress to Static Site — Build Pipeline
# Usage: make build       (full pipeline)
#        make generate    (generate only)
#        make optimize    (optimize only)
#        make validate    (all validation)
#        make help        (show targets)

SHELL := /bin/bash
OUTPUT_DIR ?= ./public
STATIC_DIR ?= ./static-output
WORKERS ?= 4

.PHONY: help build generate optimize validate validate-source test-csp \
        spell-check deploy-local clean install purge-kv-cache

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
	python3 scripts/markdown_exporter.py $(STATIC_DIR)
	python3 scripts/markdown_api.py $(STATIC_DIR)

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

# ─── Optimisation ─────────────────────────────────────────────────

optimize-images: ## Optimise images (AVIF/WebP)
	python3 scripts/optimize_images.py $(OUTPUT_DIR) --workers $(WORKERS)
	python3 scripts/convert_images_to_picture.py $(OUTPUT_DIR)

optimize-css: ## Optimise CSS files (remove unused + minify)
	python3 scripts/optimize_css.py $(OUTPUT_DIR)
	python3 scripts/optimize_css.py $(OUTPUT_DIR) --minify-only

optimize-html: ## Optimise HTML (single-pass: SEO + pictures + perf + critical CSS + minify)
	python3 scripts/html_transformer.py $(OUTPUT_DIR)

compress: ## Brotli + Gzip pre-compression
	python3 scripts/brotli_compress.py $(OUTPUT_DIR)

optimize: optimize-images optimize-css optimize-html compress ## Run all optimisation steps

# ─── Post-Deploy ──────────────────────────────────────────────────

indexnow: ## Submit changed URLs to IndexNow
	python3 scripts/submit_indexnow.py $(OUTPUT_DIR)

changelog: ## Generate changelog page
	python3 scripts/generate_changelog.py $(OUTPUT_DIR)

stats: ## Generate stats page (requires PLAUSIBLE_SHARE_LINK)
	python3 scripts/generate_stats_page.py $(OUTPUT_DIR)

# ─── Spell Check ──────────────────────────────────────────────────

spell-check: ## Run AI spell checker (requires OLLAMA_API_CREDENTIALS)
	python3 scripts/ollama_spell_checker.py $(OUTPUT_DIR)

# ─── Local Development ───────────────────────────────────────────

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
