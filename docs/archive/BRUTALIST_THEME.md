# Brutalist Theme Implementation

Inspired by [justfuckingusecloudflare.com](https://justfuckingusecloudflare.com), this brutalist dark theme has been integrated into your static site generator.

## What's Included

### Design Elements
- **Dark color scheme**: Background `#0a0a0a`, text `#fafafa`
- **Orange accent**: `#f6821f` for links, buttons, and highlights
- **Noise texture overlay**: Subtle grain effect for visual interest
- **Bold typography**:
  - Headings: Anton (uppercase, bold)
  - Body: Space Grotesk (clean, modern)
  - Code: JetBrains Mono (monospace)
- **Minimalist UI**: Sharp borders, no rounded corners, high contrast
- **Custom selection color**: Orange background when selecting text

### Files Modified

1. **`brutalist-theme.css`** (NEW)
   - Complete CSS theme with all styling rules
   - Loaded from Google Fonts API for Anton, Space Grotesk, and JetBrains Mono

2. **`wp_to_static_generator.py`** (MODIFIED)
   - Added `add_brutalist_theme_css()` method to inject CSS into generated pages
   - Updated theme-color meta tag to `#0a0a0a` (dark)
   - Changed Utterances comments theme from `github-light` to `github-dark`

3. **`brutalist-theme-demo.html`** (NEW)
   - Demo page to preview the theme
   - Open in browser: `open brutalist-theme-demo.html`

## How It Works

When you run the static site generator, it will:

1. Process HTML from WordPress
2. Inject the brutalist theme CSS into the `<head>` section
3. Update the theme-color meta tag for mobile browsers
4. Apply dark theme to Utterances comments

The CSS uses `!important` declarations to override WordPress's existing styles, ensuring the brutalist aesthetic takes precedence.

## Next Steps

### 1. Preview the Theme
Open `brutalist-theme-demo.html` in your browser to see a preview:
```bash
open brutalist-theme-demo.html
```

### 2. Generate Your Site with the New Theme
When ready, regenerate your static site:
```bash
export WP_AUTH_TOKEN="your_token_here"
python3 wp_to_static_generator.py ./static-output
```

### 3. Deploy to Staging
Test on your staging site first:
```bash
python3 deploy_static_site.py full ./static-output --git
```

Your staging site at `jkcoukblog.pages.dev` will now use the brutalist theme.

### 4. Deploy to Production
Once you're happy with the staging site, push to production:
```bash
# Commit and push changes
git add brutalist-theme.css wp_to_static_generator.py
git commit -m "Add brutalist dark theme inspired by justfuckingusecloudflare.com

Co-Authored-By: Warp <agent@warp.dev>"
git push origin main

# Trigger deployment workflow
gh workflow run deploy-static-site.yml
```

## Customization

### Colors
Edit `brutalist-theme.css` to customize colors:
```css
:root {
  --bg-dark: #0a0a0a;        /* Background color */
  --text-light: #fafafa;     /* Text color */
  --accent-orange: #f6821f;  /* Links, buttons, highlights */
  --gray-mid: #404040;       /* Borders */
  --gray-light: #666666;     /* Meta text */
}
```

### Typography
To use different fonts, modify the Google Fonts import in `brutalist-theme.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=YourFont&display=swap');
```

### Noise Intensity
Adjust the noise overlay opacity in `brutalist-theme.css`:
```css
body::before {
  opacity: 0.03;  /* Lower = less noise, Higher = more noise */
}
```

## Disable the Theme

If you want to temporarily disable the theme without removing the code:

1. Rename `brutalist-theme.css` to `brutalist-theme.css.disabled`
2. Regenerate your site

The generator will skip CSS injection if the file doesn't exist.

## Comparison

| Element | Before | After |
|---------|--------|-------|
| Background | White (#ffffff) | Dark (#0a0a0a) |
| Text | Dark gray | Light (#fafafa) |
| Headings | Default WordPress font | Anton (uppercase) |
| Links | Blue | Orange (#f6821f) |
| Code | Light background | Dark with orange text |
| Comments | GitHub Light theme | GitHub Dark theme |
| Borders | Rounded | Sharp, minimalist |

## Performance Impact

- **CSS file size**: ~11 KB uncompressed
- **Font loading**: 3 Google Fonts families
- **Rendering**: No JavaScript required, pure CSS
- **Mobile**: Optimized with responsive breakpoints

The CSS is injected inline in each page, so there's no additional HTTP request. The fonts are loaded from Google Fonts CDN with preconnect hints for optimal performance.

## Browser Support

The theme uses modern CSS features but degrades gracefully:
- CSS Custom Properties (variables) - all modern browsers
- `::selection` pseudo-element - all browsers
- SVG data URLs - all browsers
- CSS Grid & Flexbox - all modern browsers

Tested on:
- Chrome/Edge (Chromium)
- Firefox
- Safari

## Inspiration

This theme is inspired by the brutalist aesthetic of [justfuckingusecloudflare.com](https://justfuckingusecloudflare.com), which features:
- High contrast dark mode
- Bold typography
- Minimal, functional design
- No unnecessary decorations
- Orange accent color
- Noise texture overlay

## Troubleshooting

### Theme not applying
- Ensure `brutalist-theme.css` exists in the same directory as `wp_to_static_generator.py`
- Check the generator output for the message: `🎨 Added brutalist theme CSS`

### Fonts not loading
- Check your internet connection (fonts load from Google Fonts CDN)
- Verify the `@import` statement in the CSS is correct

### CSS conflicts
- The theme uses `!important` extensively to override WordPress styles
- If you see conflicts, adjust specificity in `brutalist-theme.css`

### Mobile issues
- The theme is responsive with breakpoints at 768px
- Test on actual devices, not just browser DevTools

## Credits

- Theme inspired by: [justfuckingusecloudflare.com](https://justfuckingusecloudflare.com)
- Fonts: Anton, Space Grotesk, JetBrains Mono (Google Fonts)
- Implementation: Automated via Warp AI Agent
