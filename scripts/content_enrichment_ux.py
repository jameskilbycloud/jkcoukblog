#!/usr/bin/env python3
"""
Content-enrichment UX — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the eighth cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

Two independent per-page passes, both fully stateless: adding a copy-code
button (+ its inline click handler) to every code block, and adding a
visible reading-time/word-count indicator to full-article entry-meta
sections.

WordPressStaticGenerator.process_html() drives these via a
ContentEnrichmentUX instance (self.enrichment); see that method for where
they run. Behaviour is unchanged from the pre-extraction version — this is
a pure move, not a rewrite.
"""


class ContentEnrichmentUX:
    """Copy-code buttons and the reading-time/word-count indicator for a
    single page's already-parsed soup. Fully stateless: takes no
    constructor arguments."""

    def add_copy_code_button(self, soup):
        """Add copy code button to all code blocks"""

        # Find all pre > code blocks (standard code block pattern)
        code_blocks = soup.find_all('pre')

        if not code_blocks:
            return

        button_count = 0

        for pre in code_blocks:
            # Skip if already has copy button wrapper
            if pre.parent and 'code-block-wrapper' in pre.parent.get('class', []):
                continue

            # Wrap pre in a div with relative positioning
            wrapper = soup.new_tag('div')
            wrapper['class'] = 'code-block-wrapper'
            wrapper['style'] = 'position: relative; margin: 1em 0;'

            # Create copy button
            button = soup.new_tag('button')
            button['class'] = 'copy-code-button'
            button['aria-label'] = 'Copy code to clipboard'
            button['style'] = '''position: absolute; top: 8px; right: 8px;
                padding: 6px 12px; background: #2d3748; color: #fff;
                border: 1px solid #4a5568; border-radius: 4px;
                cursor: pointer; font-size: 12px; font-family: sans-serif;
                opacity: 0.8; transition: opacity 0.2s, background 0.2s;
                z-index: 10;'''
            button.string = '📋 Copy'

            # Insert wrapper before pre
            pre.insert_before(wrapper)
            # Move pre into wrapper
            wrapper.append(pre.extract())
            # Add button to wrapper
            wrapper.append(button)

            button_count += 1

        if button_count > 0:
            # Add JavaScript for copy functionality
            script = soup.new_tag('script')
            script.string = '''
(function() {
    document.querySelectorAll('.copy-code-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var pre = this.previousElementSibling;
            var code = pre.querySelector('code') || pre;
            var text = code.textContent || code.innerText;

            // Copy to clipboard
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function() {
                    // Success feedback
                    button.textContent = '✅ Copied!';
                    button.style.background = '#48bb78';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                        button.style.background = '#2d3748';
                    }, 2000);
                }).catch(function() {
                    button.textContent = '❌ Failed';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                    }, 2000);
                });
            } else {
                // Fallback for older browsers
                var textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                    button.textContent = '✅ Copied!';
                    button.style.background = '#48bb78';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                        button.style.background = '#2d3748';
                    }, 2000);
                } catch (err) {
                    button.textContent = '❌ Failed';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                    }, 2000);
                }
                document.body.removeChild(textarea);
            }
        });

        // Hover effects
        button.addEventListener('mouseenter', function() {
            this.style.opacity = '1';
            this.style.background = '#4a5568';
        });
        button.addEventListener('mouseleave', function() {
            this.style.opacity = '0.8';
            this.style.background = '#2d3748';
        });
    });
})();
'''

            # Add script to end of body
            if soup.body:
                soup.body.append(script)
                print(f"   📋 Added copy buttons to {button_count} code blocks")
        else:
            print("   ℹ️  No code blocks found to add copy buttons")

    def add_reading_time_indicator(self, soup):
        """Add visible reading time and word count to the entry-meta section.

        Iterates over all <article> elements. Only processes articles that have
        an .entry-content div (i.e. full single-post content). Post cards on
        list pages (homepage, archives) lack .entry-content and are skipped.
        """
        articles = soup.find_all('article')
        if not articles:
            print("   ℹ️  Skipping reading time indicator - no articles found")
            return

        added = 0
        for article in articles:
            # Only process articles with full content - skip excerpt cards
            entry_content = article.find(class_='entry-content')
            if not entry_content:
                continue

            # Skip if reading time already present in this article
            if article.find(class_='reading-time'):
                continue

            # Find entry-meta within this specific article
            entry_meta = article.find('div', class_=lambda x: x and 'entry-meta' in x)
            if not entry_meta:
                continue

            # Extract text from entry-content only
            content_copy = entry_content.__copy__()
            for tag in content_copy(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                tag.decompose()
            text = ' '.join(content_copy.get_text(separator=' ', strip=True).split())

            if len(text) < 100:
                continue

            # Calculate word count and reading time
            word_count = len(text.split())
            reading_minutes = max(1, round(word_count / 200))  # 200 words per minute average

            # Create reading time span
            reading_time_span = soup.new_tag('span')
            reading_time_span['class'] = 'reading-time'
            reading_time_span['style'] = 'color: #718096;'

            # Add separator
            separator = soup.new_tag('span')
            separator.string = ' • '
            reading_time_span.append(separator)

            # Add reading time icon and text
            time_icon = soup.new_tag('span')
            time_icon['style'] = 'margin-right: 4px;'
            time_icon.string = '📖'
            reading_time_span.append(time_icon)

            # Reading time text
            time_text = soup.new_tag('span')
            time_text.string = f'{reading_minutes} min read'
            reading_time_span.append(time_text)

            # Add word count
            word_count_text = soup.new_tag('span')
            word_count_text['style'] = 'margin-left: 4px; color: #a0aec0;'
            word_count_text.string = f'({word_count:,} words)'
            reading_time_span.append(word_count_text)

            # Append to entry-meta
            entry_meta.append(reading_time_span)
            added += 1
            print(f"   📖 Added reading time: {reading_minutes} min ({word_count:,} words)")

        if added == 0 and not any(a.find(class_='entry-content') for a in articles):
            print("   ℹ️  Skipping reading time indicator - no articles with entry-content (list page)")
