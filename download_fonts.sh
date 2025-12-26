#!/bin/bash
# Download Google Fonts for Self-Hosting
# Fonts needed: Anton, JetBrains Mono, Space Grotesk

set -e

FONTS_DIR="public/assets/fonts"
mkdir -p "$FONTS_DIR"

echo "📥 Downloading Google Fonts..."

# Download fonts using google-webfonts-helper API
# This gets the actual font files without needing to parse CSS

# Anton (Regular 400)
echo "  Downloading Anton..."
curl -sL "https://gwfh.mranftl.com/api/fonts/anton?download=zip&subsets=latin&variants=regular" -o /tmp/anton.zip
unzip -q -o /tmp/anton.zip -d /tmp/anton
cp /tmp/anton/*.woff2 "$FONTS_DIR/" 2>/dev/null || true
cp /tmp/anton/*.woff "$FONTS_DIR/" 2>/dev/null || true

# JetBrains Mono (Regular 400, Bold 700)
echo "  Downloading JetBrains Mono..."
curl -sL "https://gwfh.mranftl.com/api/fonts/jetbrains-mono?download=zip&subsets=latin&variants=regular,700" -o /tmp/jetbrains.zip
unzip -q -o /tmp/jetbrains.zip -d /tmp/jetbrains
cp /tmp/jetbrains/*.woff2 "$FONTS_DIR/" 2>/dev/null || true
cp /tmp/jetbrains/*.woff "$FONTS_DIR/" 2>/dev/null || true

# Space Grotesk (Regular 400, Medium 500, Bold 700)
echo "  Downloading Space Grotesk..."
curl -sL "https://gwfh.mranftl.com/api/fonts/space-grotesk?download=zip&subsets=latin&variants=regular,500,700" -o /tmp/space-grotesk.zip
unzip -q -o /tmp/space-grotesk.zip -d /tmp/space-grotesk
cp /tmp/space-grotesk/*.woff2 "$FONTS_DIR/" 2>/dev/null || true
cp /tmp/space-grotesk/*.woff "$FONTS_DIR/" 2>/dev/null || true

# Cleanup
rm -rf /tmp/anton /tmp/anton.zip
rm -rf /tmp/jetbrains /tmp/jetbrains.zip
rm -rf /tmp/space-grotesk /tmp/space-grotesk.zip

echo "✅ Fonts downloaded to $FONTS_DIR"
ls -lh "$FONTS_DIR"
