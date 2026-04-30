# Markdown Content API

Generated: 2026-04-30 11:01:03

## Endpoints

### Posts
- All posts: `/api/posts.json`
- Paginated: `/api/posts-page-{page}.json`
- Single post: `/api/posts/{slug}.json`

### Categories
- All categories: `/api/categories/index.json`
- Category posts: `/api/categories/{slug}.json`

### Tags
- All tags: `/api/tags/index.json`
- Tag posts: `/api/tags/{slug}.json`

### Archive
- All months: `/api/archive/index.json`
- Month posts: `/api/archive/{year}-{month}.json`

## Content Formats
- Markdown: `/markdown/posts/{slug}.md`
- HTML: `/{year}/{month}/{slug}/`