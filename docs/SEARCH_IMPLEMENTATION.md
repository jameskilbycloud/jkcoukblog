# Adding Search Functionality to Your Static Site

This guide shows you how to add a powerful, fast, client-side search feature to your static blog generated from WordPress.

## 🎯 Overview

The search system consists of:
- **Search Index Generator**: Python script that creates a searchable JSON index from your static HTML files
- **Client-side Search**: JavaScript using Fuse.js for fast, fuzzy searching
- **Automatic Integration**: Seamlessly integrated into your existing WordPress-to-static pipeline

## ✨ Features

- ⚡ **Fast Client-Side Search**: No server required, instant results
- 🔍 **Fuzzy Search**: Finds results even with typos
- 🏷️ **Multi-field Search**: Searches titles, content, categories, and tags
- 🎨 **Beautiful UI**: Modal overlay with highlighted search terms
- ⌨️ **Keyboard Shortcuts**: Ctrl+K (Cmd+K on Mac) to quickly open search
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🔒 **Privacy Friendly**: No external services, all data stays local

## 🚀 Quick Start

### Step 1: Generate Your Static Site with Search Index

Your WordPress-to-static generator has been updated to automatically create search indexes. Just run it as usual:

```bash
# Set your auth token
export WP_AUTH_TOKEN="your_wordpress_auth_token"

# Generate static site (now includes search index)
python3 wp_to_static_generator.py ./public
```

This will now create:
- `public/search-index.json` - Full search index with formatting
- `public/search-index.min.json` - Minified version for production

### Step 2: Add Search JavaScript

Copy the search script to your static site:

```bash
# Create js directory if it doesn't exist
mkdir -p public/js

# Copy the search JavaScript
cp public/js/search.js public/js/search.js
```

### Step 3: Update Your HTML Template

Add the search script to your site's HTML. The script will automatically detect your existing WordPress search form.

Add this before the closing `</body>` tag:

```html
<script src="/js/search.js"></script>
```

### Step 4: Test Locally

```bash
# Test the search generation and functionality
python3 test_search.py

# Start local server for testing
python3 test_search.py --server
```

Open http://localhost:8000 and test the search by:
1. Clicking on the search input
2. Typing some keywords
3. Or pressing Ctrl+K (Cmd+K on Mac) to quickly open search

### Step 5: Deploy

Deploy your updated static site to your hosting platform (Cloudflare Pages, Netlify, etc.). The search functionality will work immediately.

## 📁 File Structure

```
your-project/
├── wp_to_static_generator.py      # Updated with search generation
├── generate_search_index.py       # Standalone search index generator
├── test_search.py                 # Test script
├── search-integration.html        # HTML integration examples
└── public/                        # Generated static site
    ├── search-index.json          # Full search index
    ├── search-index.min.json      # Minified search index
    ├── js/
    │   └── search.js              # Search functionality
    └── [your other static files]
```

## ⚙️ Advanced Configuration

### Customizing Search Behavior

Edit `public/js/search.js` to customize:

```javascript
const fuseOptions = {
    keys: [
        { name: 'title', weight: 0.4 },        // Title importance
        { name: 'description', weight: 0.3 },  // Description importance
        { name: 'content', weight: 0.2 },      // Content importance
        { name: 'categories', weight: 0.05 },  // Category importance
        { name: 'tags', weight: 0.05 }         // Tag importance
    ],
    threshold: 0.4,  // Lower = more strict, Higher = more fuzzy
    minMatchCharLength: 2  // Minimum characters to search
};
```

### Styling the Search Interface

The search interface is fully styled with CSS included in the JavaScript file. You can customize colors, sizes, and animations by modifying the `addSearchStyles()` function in `search.js`.

### Manual Search Index Generation

If you need to generate a search index separately:

```bash
# Generate search index from existing static site
python3 generate_search_index.py public --output search-index.json --base-url https://jameskilby.co.uk
```

## 🔧 Integration with Your Current Workflow

### GitHub Actions Integration

Your existing GitHub Actions workflow will automatically include search functionality since it's now built into the WordPress-to-static generator.

### Cloudflare Pages Integration

No additional configuration needed. The search files will be deployed automatically with your static site.

## 🎨 Search Interface

The search interface includes:

- **Search Overlay**: Full-screen modal that appears when searching
- **Live Results**: Results appear as you type
- **Highlighted Matches**: Search terms are highlighted in results
- **Rich Metadata**: Shows categories, tags, and publication dates
- **Keyboard Navigation**: Use arrow keys to navigate results
- **Mobile Optimized**: Touch-friendly on mobile devices

## 📊 Performance

- **Index Size**: Typically 50-200KB for a blog with 100+ posts
- **Load Time**: Index loads only when search is first used
- **Search Speed**: Near-instant results with Fuse.js
- **Browser Support**: Works in all modern browsers

## 🔍 Search Features

### What Can Be Searched

- Post and page titles
- Post content and excerpts  
- Categories and tags
- Meta descriptions

### Search Capabilities

- **Fuzzy Matching**: Finds "homelab" when you type "homelb"
- **Multi-word Search**: "docker networking" finds posts about both topics
- **Category/Tag Search**: Find all posts in specific categories
- **Partial Matching**: "AI" finds "Artificial Intelligence"

## 🐛 Troubleshooting

### Search Not Working?

1. **Check browser console** for JavaScript errors
2. **Verify search index exists** at `/search-index.min.json`
3. **Check search input detection** - ensure your form has class `.search-field` or name `s`
4. **Test Fuse.js loading** from CDN

### Common Issues

**Search overlay doesn't appear:**
- Ensure search.js is loaded correctly
- Check that your search input is detected

**No search results:**
- Verify search-index.min.json is accessible
- Check that the index contains data
- Try different search terms

**Styling issues:**
- The search interface uses inline styles to avoid conflicts
- Modify the `addSearchStyles()` function for custom styling

### Debug Mode

Add this to your browser console to enable debug logging:

```javascript
localStorage.setItem('search-debug', 'true');
```

## 🚀 Alternative Search Solutions

If you prefer different approaches, here are other options:

### 1. Algolia Integration

For larger sites, consider Algolia:

```javascript
// Replace Fuse.js with Algolia client
const searchClient = algoliasearch('YourApplicationID', 'YourSearchOnlyAPIKey');
```

### 2. Lunr.js Alternative

Replace Fuse.js with Lunr.js for different search behavior:

```javascript
// Use Lunr.js instead of Fuse.js
const idx = lunr(function () {
    this.ref('url');
    this.field('title');
    this.field('content');
    // ... configure lunr
});
```

### 3. Server-Side Search

For very large sites, consider server-side search with:
- Elasticsearch
- Solr  
- Custom API endpoints

## 📈 Monitoring Search Usage

Track search usage with your analytics:

```javascript
// Add to search.js performSearch() function
gtag('event', 'search', {
    search_term: query,
    results_count: results.length
});
```

## 🔄 Updating Search Content

The search index is automatically regenerated every time you run your WordPress-to-static generation process. No manual updates needed!

## 🎉 That's It!

Your static site now has powerful search functionality that:
- ✅ Works without a server
- ✅ Is fast and responsive  
- ✅ Provides great user experience
- ✅ Updates automatically with your content
- ✅ Is privacy-friendly
- ✅ Works on all devices

## 📞 Support

If you run into issues:

1. Check the troubleshooting section above
2. Run the test script: `python3 test_search.py`
3. Look at the browser console for errors
4. Verify all files are in the correct locations

The search functionality is designed to be robust and work with minimal configuration. Just generate, deploy, and enjoy fast searching on your static site!