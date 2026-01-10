# Blog Update Summary - FOLDING PLAMO FACTORY Pattern

## Changes Implemented

### 1. Tag System Updated
**File**: `rijmenbaskara/views.py`
- Changed `TAG_CHOICES` from generic tags to Warhammer-specific:
  - `40k`, `30k`, `Age of Sigmar`

### 2. Template Filter for Date Formatting
**Files Created**:
- `rijmenbaskara/templatetags/__init__.py`
- `rijmenbaskara/templatetags/article_extras.py`

**Filter**: `format_article_date`
- Converts timestamp `20251220165204` → `December 20`
- Format: "F j" (Month day)
- Usage: `{{ article.created_at|format_article_date }}`

### 3. Related Articles Sidebar
**File**: `rijmenbaskara/views.py` - `article_detail()` function

**Logic**:
- Finds articles with matching tags (up to 3)
- If fewer than 3, fills remaining slots with newest articles
- Excludes current article
- Sorted by `created_at` descending

**Template**: `templates/article_detail.html`
- Added sidebar layout with two-column grid
- Related articles module showing:
  - Article title (linked)
  - Date formatted as "Month day"
  - Tags as mini badges
- Categories/tags cloud module
- "Back to all articles" link

### 4. Year-Grouped Article List
**Template**: `templates/articles.html`

**Structure**:
- Articles grouped by year
- Each year has heading (e.g., "2025")
- All year blocks expanded by default
- Each article card shows:
  - Title (linked)
  - Date as "Month day"
  - Clickable tag badges

### 5. Clickable Tags Everywhere
**Changes**:
- Article list: Tags are now `<a>` links filtering by tag
- Article detail: Tags link to filtered view
- Related sidebar: Mini tags display
- All tags link to: `{% url 'articles' %}?tag={{ tag }}`

### 6. Inline Images Support
**CSS**: `static/css/articles.css`

Added responsive image styling:
```css
.article-detail__body img {
  max-width: 100%;
  height: auto;
  margin: 20px 0;
  border: 1px solid var(--rule);
  border-radius: 2px;
}
```

**Usage**: Images in `body_html` field automatically responsive

## CSS Additions

**File**: `static/css/articles.css`

### New Classes:
1. **Sidebar Layout**
   - `.article-detail-container` - 2-column grid
   - `.article-main` - Main content area
   - `.article-sidebar` - Sticky sidebar
   - `.sidebar-module` - Sidebar sections
   - `.sidebar-title` - Section headings

2. **Related Articles**
   - `.related-articles` - Container
   - `.related-item` - Article wrapper
   - `.related-link` - Clickable area
   - `.related-title` - Article title
   - `.related-meta` - Date + tags area
   - `.related-date` - Date text
   - `.related-tags` - Tags container
   - `.mini-tag` - Small tag badges

3. **Tags Cloud**
   - `.tags-cloud` - Flex container
   - `.cloud-tag` - Individual tags with hover

4. **Year-Grouped List**
   - `.year-block` - Year section wrapper
   - `.year-heading` - Year title (e.g., "2025")
   - `.year-articles` - Articles container
   - `.article-card` - Individual article card
   - `.article-card__main` - Content area
   - `.article-card__title` - Article title
   - `.article-card__meta` - Date + tags row
   - `.article-date` - Formatted date
   - `.article-card__tags` - Tags container
   - `.article-tag` - Individual tag badge
   - `.article-card__edit` - Edit button (staff only)

5. **Responsive Behavior**
   - Sidebar stacks below content on mobile (<720px)
   - Tags wrap properly
   - Cards maintain readability

## Media Configuration

**Already Configured** in `rijmenbaskara/settings.py`:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'articles_store'
```

**URLs** in `rijmenbaskara/urls.py`:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### For Image Uploads in Rich Text:
Current system uses `body_html` field. To add inline images:

**Option 1**: Use CKEditor/TinyMCE (if not already)
```python
# pip install django-ckeditor
# Add to INSTALLED_APPS: 'ckeditor', 'ckeditor_uploader'
# Configure CKEDITOR_UPLOAD_PATH in settings
```

**Option 2**: Manual Markdown (if preferred)
- Users write: `![Alt text](/media/images/photo.jpg)`
- Install: `pip install markdown`
- Render with: `{{ article.body_markdown|markdown|safe }}`

## Testing Checklist

### Article Detail Page:
- [ ] Related articles show (max 3)
- [ ] Related articles prefer same-tag matches
- [ ] Dates display as "Month day" format
- [ ] Tags are clickable badges
- [ ] Sidebar sticky on scroll
- [ ] Images in body content are responsive
- [ ] "Back to articles" link works

### Article List Page:
- [ ] Posts grouped by year
- [ ] Year headings display correctly
- [ ] All year blocks visible (no collapse)
- [ ] Each post shows formatted date
- [ ] Tags are clickable
- [ ] Tag filtering works from list page
- [ ] Search functionality preserved

### Cross-Page:
- [ ] Clicking tag from detail page filters list
- [ ] Clicking tag from list page filters results
- [ ] Tag badges consistent styling everywhere
- [ ] No 404s or broken links

## Migration Notes

**No database migrations needed** - This project uses JSON file storage for articles, not Django models.

## Performance Notes

The `article_detail` view loads all articles to compute related posts. For large article counts (100+), consider:
- Caching related posts
- Limiting `_load_articles()` to recent articles only
- Using database models with indexed queries

## Future Enhancements

1. **Prev/Next Navigation**: Add links to adjacent articles by date
2. **Reading Time**: Calculate from body_html length
3. **Search Highlighting**: Highlight search terms in results
4. **Lazy Load Images**: Add loading="lazy" to body images
5. **Tag Popularity**: Show article count per tag in cloud
