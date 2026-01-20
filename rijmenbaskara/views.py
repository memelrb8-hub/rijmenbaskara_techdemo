from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import json
import re
import os
from datetime import datetime
import zipfile
import io

# File-based article storage (local file management)
ARTICLES_DIR = Path(settings.BASE_DIR) / "articles_store"
# Only create directories when not on Vercel (read-only filesystem)
if not os.environ.get('VERCEL'):
    ARTICLES_DIR.mkdir(exist_ok=True)
    ARTICLES_COVERS_DIR = ARTICLES_DIR / "covers"
    ARTICLES_COVERS_DIR.mkdir(exist_ok=True)
else:
    ARTICLES_COVERS_DIR = ARTICLES_DIR / "covers"


def _slugify(value: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9-]+', '-', value.strip().lower()).strip('-')
    return slug or "article"


def _article_path(article_id: str) -> Path:
    return ARTICLES_DIR / f"{article_id}.json"


def _load_articles():
    items = []
    for path in ARTICLES_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data.setdefault("id", path.stem)
            items.append(data)
        except Exception:
            continue
    return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)


def _load_article(article_id: str):
    path = _article_path(article_id)
    if not path.exists():
        raise Http404("Article not found")
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("id", article_id)
    return data


def _load_projects():
    """Load all projects from projects_store directory"""
    projects_file = PROJECTS_DIR / "seed_projects.json"
    if projects_file.exists():
        try:
            data = json.loads(projects_file.read_text(encoding="utf-8"))
            return sorted(data, key=lambda x: x.get("created_at", ""), reverse=True)
        except Exception:
            pass
    return []


def _load_project(project_id: str):
    """Load a single project by ID"""
    projects = _load_projects()
    for project in projects:
        if project.get("id") == project_id:
            return project
    raise Http404("Project not found")


def _save_projects(projects):
    """Save projects list to JSON file"""
    if os.environ.get('VERCEL'):
        return  # Cannot write on read-only filesystem
    projects_file = PROJECTS_DIR / "seed_projects.json"
    projects_file.write_text(json.dumps(projects, indent=2), encoding="utf-8")


def _save_project_image(uploaded_file):
    """Save an uploaded image to static/images and return the filename"""
    import hashlib
    from django.core.files.storage import default_storage
    
    # Generate unique filename
    ext = Path(uploaded_file.name).suffix.lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    hash_part = hashlib.md5(uploaded_file.read()).hexdigest()[:8]
    uploaded_file.seek(0)  # Reset file pointer
    filename = f"project_{timestamp}_{hash_part}{ext}"
    
    # Save to static/images (disabled on Vercel)
    if os.environ.get('VERCEL'):
        return None  # Cannot save on read-only filesystem
    
    images_dir = Path(settings.BASE_DIR) / "static" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    filepath = images_dir / filename
    
    with open(filepath, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    return filename


def _ensure_staff(request):
    # On Vercel, request.user doesn't exist (no auth middleware)
    if not hasattr(request, 'user') or not request.user.is_authenticated or not request.user.is_staff:
        if hasattr(request, 'user'):
            messages.error(request, "Admins only.")
        return False
    return True

# Preset tags
TAG_CHOICES = [
    "40k", "30k", "Age of Sigmar"
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
WORKS_MAX_ITEMS = 10
GALLERIES_DIR = Path(settings.BASE_DIR) / "static" / "images" / "galleries"
PROJECTS_DIR = Path(settings.BASE_DIR) / "projects_store"
# Only create directory on local/Docker, not Vercel
if not os.environ.get('VERCEL'):
    PROJECTS_DIR.mkdir(exist_ok=True)

def contact(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        
        if email and message:
            # Compose the email
            subject = f'New Contact Form Message from {email}'
            full_message = f'From: {email}\n\nMessage:\n{message}'
            
            try:
                # Send email
                send_mail(
                    subject,
                    full_message,
                    email,  # From email
                    ['rijmenbaskara@gmail.com'],  # To email
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                messages.error(request, f'Failed to send message. Please try again later.')
            
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'contact.html')

def home(request):
    projects = _load_projects()[:6]  # Get first 6 projects for homepage
    hero_images = []
    
    # Use project images for hero carousel
    for project in projects:
        for image in project.get('images', [])[:2]:  # Take up to 2 images per project
            hero_images.append({
                'src': f'images/{image}'
            })
    
    # Prepare works items from projects
    works_items = []
    for project in projects:
        if project.get('images'):
            works_items.append({
                'title': project.get('title', ''),
                'slug': project.get('id', ''),
                'thumb': f"images/{project['images'][0]}",
                'category': project.get('category', '')
            })
    
    return render(request, 'home.html', {
        "works_items": works_items,
        "hero_images": hero_images if hero_images else works_items
    })

def works(request):
    projects = _load_projects()
    # On Vercel, request.user doesn't exist (no auth middleware)
    is_admin = hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff
    return render(request, 'works.html', {
        "projects": projects,
        "is_admin": is_admin,
    })

def articles(request):
    items = _load_articles()
    active_tag = request.GET.get('tag', '').strip()
    query = request.GET.get('q', '').strip().lower()
    if active_tag:
        items = [a for a in items if active_tag in (a.get("tags") or [])]
    if query:
        items = [
            a for a in items
            if query in (a.get("title") or "").lower()
            or query in (a.get("subtitle") or "").lower()
            or query in " ".join(a.get("tags") or []).lower()
        ]

    year_groups = {}
    for art in items:
        year = (art.get("created_at") or "")[:4] or "Unknown"
        year_groups.setdefault(year, []).append(art)
    ordered_years = sorted(year_groups.keys(), reverse=True)
    year_list = [(year, year_groups[year]) for year in ordered_years]
    return render(request, 'articles.html', {
        "year_groups": year_groups,
        "ordered_years": ordered_years,
        "year_list": year_list,
        "active_tag": active_tag,
        "tag_choices": TAG_CHOICES,
        "articles_query": request.GET.get('q', ''),
    })

def about(request):
    return render(request, 'about.html')


def article_detail(request, article_id):
    article = _load_article(article_id)
    all_articles = _load_articles()
    
    # Get article tags for matching
    current_tags = set(article.get("tags") or [])
    current_slug = article.get("slug") or article_id
    
    # Find related articles (same tags, excluding current)
    related = []
    other_articles = []
    
    for art in all_articles:
        art_slug = art.get("slug") or art.get("file", "").split("/")[-1].replace(".json", "")
        if art_slug == current_slug:
            continue
            
        art_tags = set(art.get("tags") or [])
        if current_tags & art_tags:  # Has common tags
            related.append(art)
        else:
            other_articles.append(art)
    
    # Sort by date (newest first) - using created_at timestamp
    related.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    other_articles.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    
    # Take up to 3 related, fill remaining with other articles
    related_posts = related[:3]
    if len(related_posts) < 3:
        related_posts.extend(other_articles[:3 - len(related_posts)])
    
    return render(request, 'article_detail.html', {
        "article": article,
        "related_posts": related_posts,
        "tag_choices": TAG_CHOICES
    })

def add_article(request):
    if not _ensure_staff(request):
        return redirect('articles')
    return _article_form(request)


def edit_article(request, article_id):
    if not _ensure_staff(request):
        return redirect('articles')
    return _article_form(request, article_id=article_id, is_edit=True)


def manage_articles(request):
    if not _ensure_staff(request):
        return redirect('articles')
    items = _load_articles()
    return render(request, 'manage_articles.html', {"articles": items})


def export_content_backup(request):
    """
    Admin-only: Create a ZIP file containing all content files
    (articles, images, projects) for backup and easy restoration.
    """
    if not _ensure_staff(request):
        return redirect('articles')
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add articles_store directory (JSON files and covers)
        articles_dir = Path(settings.BASE_DIR) / "articles_store"
        if articles_dir.exists():
            for file_path in articles_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(settings.BASE_DIR)
                    zip_file.write(file_path, arcname)
        
        # Add static/images directory (galleries, projects, etc.)
        images_dir = Path(settings.BASE_DIR) / "static" / "images"
        if images_dir.exists():
            for file_path in images_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(settings.BASE_DIR)
                    zip_file.write(file_path, arcname)
        
        # Add projects_store directory
        projects_dir = Path(settings.BASE_DIR) / "projects_store"
        if projects_dir.exists():
            for file_path in projects_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(settings.BASE_DIR)
                    zip_file.write(file_path, arcname)
        
        # Add a README for restoration instructions
        readme_content = """# Content Backup - Rijmen & Baskara

## Backup Date: {date}

## Contents:
- articles_store/: All article JSON files and cover images
- static/images/: Gallery images, project images, and other static images
- projects_store/: Project data files

## Restoration Instructions:

1. Extract this ZIP file
2. Copy the folders to your project root directory:
   - articles_store/ -> <project_root>/articles_store/
   - static/images/ -> <project_root>/static/images/
   - projects_store/ -> <project_root>/projects_store/

3. Ensure proper permissions (on Linux/Mac):
   chmod -R 755 articles_store/ static/images/ projects_store/

4. Restart your Django server

All content will be immediately available.
""".format(date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
        
        zip_file.writestr('README_RESTORATION.txt', readme_content)
    
    # Prepare HTTP response
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="rijmenbaskara_backup_{timestamp}.zip"'
    
    messages.success(request, f'Backup created successfully: rijmenbaskara_backup_{timestamp}.zip')
    
    return response


def add_work(request, gallery_id="default"):
    """
    Simple server-rendered uploader for gallery items.
    Requires title, image, and thumbnail. Admin-only.
    """
    if not _ensure_staff(request):
        return redirect('works')

    gallery_id = _slugify(gallery_id)
    gallery_dir = _gallery_dir(gallery_id)
    meta_path = _gallery_meta_path(gallery_id)
    # Prevent directory creation on Vercel (read-only filesystem)
    if not os.environ.get('VERCEL'):
        gallery_dir.mkdir(parents=True, exist_ok=True)
    errors = {}
    draft_title = ""
    used_count = _gallery_item_count(gallery_id)
    limit_reached = used_count >= WORKS_MAX_ITEMS

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        draft_title = title
        image_file = request.FILES.get('image')
        thumb_file = request.FILES.get('thumbnail')

        if limit_reached:
            errors.setdefault("limit", []).append(f"Limit reached ({WORKS_MAX_ITEMS} photos). Remove one to add another.")
        if not title:
            errors.setdefault("title", []).append("Title is required.")
        if not image_file:
            errors.setdefault("image", []).append("Full image is required.")
        if not thumb_file:
            errors.setdefault("thumbnail", []).append("Thumbnail image is required.")

        def _valid_image(file_obj):
            return file_obj and Path(file_obj.name).suffix.lower() in IMAGE_EXTS

        if image_file and not _valid_image(image_file):
            errors.setdefault("image", []).append("Full image must be an image file.")
        if thumb_file and not _valid_image(thumb_file):
            errors.setdefault("thumbnail", []).append("Thumbnail must be an image file.")

        # Block saves on Vercel
        if os.environ.get('VERCEL'):
            errors.setdefault("vercel", []).append("Content editing is disabled on Vercel (read-only deployment).")

        if not errors and used_count < WORKS_MAX_ITEMS:
            new_item = _save_gallery_item(gallery_id, title, image_file, thumb_file)
            if new_item:
                messages.success(request, "Work added.")
                target = f"{reverse('works')}?gallery={gallery_id}&select={new_item.get('id')}"
                return redirect(target)

    context = {
        "errors": errors,
        "draft_title": draft_title,
        "works_used": used_count,
        "works_limit": WORKS_MAX_ITEMS,
        "limit_reached": limit_reached,
        "gallery_id": gallery_id,
    }
    return render(request, 'add_work.html', context)


def _article_form(request, article_id=None, is_edit=False):
    """
    File-backed composer: saves JSON + optional cover locally.
    """
    context = {"is_edit": is_edit, "tag_choices": TAG_CHOICES}

    existing = None
    if is_edit and article_id:
        existing = _load_article(article_id)
        context.update({
            'draft_title': existing.get("title", ""),
            'draft_subtitle': existing.get("subtitle", ""),
            'draft_body': existing.get("body_html", ""),
            'draft_tags': existing.get("tags", []) or [],
            'article_id': existing.get("id", article_id),
            'existing_cover': existing.get("cover"),
        })

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        subtitle = request.POST.get('subtitle', '').strip()
        body_html = request.POST.get('body_html', '').strip()
        tags_raw = request.POST.get('tags', '')
        tags = request.POST.getlist('tags')
        posted_id = request.POST.get('article_id')
        if posted_id:
            article_id = posted_id

        context.update({
            'draft_title': title,
            'draft_subtitle': subtitle,
            'draft_body': body_html,
            'draft_tags': tags,
            'article_id': article_id,
        })

        if not (title and body_html):
            messages.error(request, 'Please add a title and some body text.')
        else:
            if is_edit and article_id:
                record = existing or _load_article(article_id)
                record.update({
                    "title": title,
                    "subtitle": subtitle,
                    "body_html": body_html,
                    "tags": tags,
                    "slug": _slugify(title),
                })
                record["updated_at"] = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                if not record.get("created_at"):
                    record["created_at"] = record["updated_at"]
            else:
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                slug = _slugify(title)
                article_id = f"{timestamp}-{slug}"
                record = {
                    "id": article_id,
                    "title": title,
                    "subtitle": subtitle,
                    "body_html": body_html,
                    "tags": tags,
                    "slug": slug,
                    "created_at": timestamp,
                }

            cover_path = existing.get("cover") if existing else None
            if request.FILES.get('cover'):
                # Prevent writes on Vercel (read-only filesystem)
                if os.environ.get('VERCEL'):
                    messages.error(request, 'File uploads are disabled on Vercel (read-only deployment).')
                else:
                    cover_file = request.FILES['cover']
                    cover_name = f"{article_id}{Path(cover_file.name).suffix}"
                    target = ARTICLES_COVERS_DIR / cover_name
                    with target.open('wb') as fh:
                        for chunk in cover_file.chunks():
                            fh.write(chunk)
                    cover_path = f"{settings.MEDIA_URL}covers/{cover_name}"

            record["cover"] = cover_path
            record["id"] = article_id
            record["file"] = str(_article_path(article_id).relative_to(settings.BASE_DIR))

            # Prevent writes on Vercel (read-only filesystem)
            if not os.environ.get('VERCEL'):
                _article_path(article_id).write_text(
                    json.dumps(record, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                messages.success(
                    request,
                    'Draft saved locally.' if is_edit else 'Draft created locally.'
                )
            else:
                messages.error(
                    request,
                    'Content editing is disabled on Vercel (read-only deployment).'
                )
            if not is_edit:
                return redirect('manage_articles')

            context.update({
                'draft_title': record.get("title", ""),
                'draft_subtitle': record.get("subtitle", ""),
                'draft_body': record.get("body_html", ""),
                'draft_tags': record.get("tags", []) or [],
                'article_id': record.get("id", article_id),
                'existing_cover': record.get("cover"),
            })

    return render(request, 'add_article.html', context)


def _load_works_meta(meta_path: Path):
    """
    Reads optional metadata for uploads and normalizes shape.
    Supports both {"file.jpg": "Title"} and {"file.jpg": {"title": "...", "tags": [...], "genre": "...", "quality": "...", "thumb": "thumb.jpg"}}.
    """
    if not meta_path.exists():
        return {}
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    normalized = {}
    if not isinstance(data, dict):
        return normalized

    for key, val in data.items():
        title = Path(key).stem
        tags = []
        genre = None
        quality = None
        extra_tags = []
        thumb = None
        if isinstance(val, dict):
            title = val.get("title") or val.get("name") or title
            extra_tags = val.get("tags") or []
            genre = val.get("genre")
            quality = val.get("quality")
            thumb = val.get("thumb")
        elif val:
            title = str(val)

        if genre:
            tags.append(f"Genre:{genre}")
        if quality:
            tags.append(f"Quality:{quality}")
        tags.extend([t for t in extra_tags if t])
        entry = {"title": title, "tags": tags}
        if thumb:
            entry["thumb"] = thumb
        normalized[key] = entry
    return normalized


def _save_works_meta(meta_path: Path, meta: dict):
    if not os.environ.get('VERCEL'):
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _count_upload_photos(uploads_dir: Path, meta_path: Path) -> int:
    if not os.environ.get('VERCEL'):
        uploads_dir.mkdir(parents=True, exist_ok=True)
    meta = _load_works_meta(meta_path)
    thumb_files = {entry.get("thumb") for entry in meta.values() if isinstance(entry, dict) and entry.get("thumb")}
    count = 0
    for path in uploads_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        if path.name in thumb_files:
            continue
        count += 1
    return count


def _gallery_dir(gallery_id: str) -> Path:
    return GALLERIES_DIR / _slugify(gallery_id or "default")


def _gallery_meta_path(gallery_id: str) -> Path:
    return _gallery_dir(gallery_id) / "gallery.json"


def _load_gallery_meta(gallery_id: str) -> dict:
    meta_path = _gallery_meta_path(gallery_id)
    if not meta_path.exists():
        return {"items": []}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {"items": []}


def _save_gallery_meta(gallery_id: str, data: dict):
    if os.environ.get('VERCEL'):
        return  # Cannot write on read-only filesystem
    dir_path = _gallery_dir(gallery_id)
    dir_path.mkdir(parents=True, exist_ok=True)
    meta_path = _gallery_meta_path(gallery_id)
    meta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_gallery_items(gallery_id: str):
    meta = _load_gallery_meta(gallery_id)
    items = meta.get("items") or []
    return sorted(items, key=lambda x: x.get("createdAt", ""), reverse=True)


def _gallery_item_count(gallery_id: str) -> int:
    return len(_load_gallery_items(gallery_id))


def _save_gallery_item(gallery_id: str, title: str, image_file, thumb_file):
    if os.environ.get('VERCEL'):
        return None  # Cannot write on read-only filesystem
    dir_path = _gallery_dir(gallery_id)
    dir_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    base_slug = _slugify(title) or "work"

    def _store(file_obj, label):
        fname = f"{timestamp}-{base_slug}-{label}{Path(file_obj.name).suffix.lower()}"
        target = dir_path / fname
        with target.open('wb') as fh:
            for chunk in file_obj.chunks():
                fh.write(chunk)
        return fname

    image_name = _store(image_file, "full")
    thumb_name = _store(thumb_file, "thumb")
    item_id = f"{timestamp}-{base_slug}"
    item = {
        "id": item_id,
        "title": title,
        "src": f"/static/images/galleries/{_slugify(gallery_id)}/{image_name}",
        "thumb": f"/static/images/galleries/{_slugify(gallery_id)}/{thumb_name}",
        "createdAt": timestamp,
        "tags": ["Quality:Upload", "Genre:Misc"],
    }

    meta = _load_gallery_meta(gallery_id)
    items = meta.get("items") or []
    items.append(item)
    meta["items"] = items
    _save_gallery_meta(gallery_id, meta)
    return item


def _delete_gallery_item(gallery_id: str, item_id: str):
    dir_path = _gallery_dir(gallery_id)
    meta = _load_gallery_meta(gallery_id)
    items = meta.get("items") or []
    remaining = []
    deleted_paths = []
    for item in items:
        if str(item.get("id")) == str(item_id):
            if item.get("src"):
                deleted_paths.append(dir_path / Path(item["src"]).name)
            if item.get("thumb"):
                deleted_paths.append(dir_path / Path(item["thumb"]).name)
            continue
        remaining.append(item)
    meta["items"] = remaining
    _save_gallery_meta(gallery_id, meta)
    for path in deleted_paths:
        try:
            if path.exists():
                path.unlink()
        except Exception:
            continue


def _load_works_items():
    uploads_dir = Path(settings.BASE_DIR) / "static" / "images" / "works_uploads"
    if not os.environ.get('VERCEL'):
        uploads_dir.mkdir(parents=True, exist_ok=True)
    uploads_meta = _load_works_meta(uploads_dir / "works_meta.json")
    thumb_files = {entry.get("thumb") for entry in uploads_meta.values() if isinstance(entry, dict) and entry.get("thumb")}

    upload_items = []
    for path in uploads_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        if path.name in thumb_files:
            continue
        meta = uploads_meta.get(path.name) or uploads_meta.get(path.stem) or {}
        title = meta.get("title") or path.stem
        tags = list(meta.get("tags") or [])
        thumb_override = meta.get("thumb")
        if not any(tag.startswith("Quality:") for tag in tags):
            tags.append("Quality:Upload")
        if not any(tag.startswith("Genre:") for tag in tags):
            tags.append("Genre:Misc")
        thumb_path = f"images/works_uploads/{thumb_override}" if thumb_override else f"images/works_uploads/{path.name}"
        upload_items.append({
            "title": title,
            "images": [f"images/works_uploads/{path.name}"],
            "tags": tags,
            "slug": _slugify(title),
            "thumb": thumb_path,
        })

    # Sensei gallery sample from infinitecarousel (single, larger gallery)
    sensei_dir = Path(settings.BASE_DIR) / "static" / "images" / "infinitecarousel"
    sensei_images = []
    if sensei_dir.exists():
        for path in sorted(sensei_dir.glob("*")):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
                sensei_images.append(f"images/infinitecarousel/{path.name}")
    sensei_items = []
    if sensei_images:
        sensei_items.append({
            "title": "SenseiWagnibiart Gallery",
            "images": sensei_images,
            "tags": ["Quality:Showcase", "Genre:Mech", "SenseiWagnibiart"],
            "slug": _slugify("SenseiWagnibiart Gallery"),
        })

    works_items = []
    for item in sensei_items + upload_items:
        item = item.copy()
        if "slug" not in item:
            item["slug"] = _slugify(item["title"])
        item["thumb"] = item.get("thumb") or (item["images"][0] if item.get("images") else None)
        works_items.append(item)
    return works_items


def _load_infinite_images():
    images_dir = Path(settings.BASE_DIR) / "static" / "images" / "infinitecarousel"
    if not images_dir.exists():
        return []
    items = []
    for path in sorted(images_dir.glob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            items.append({"src": f"images/infinitecarousel/{path.name}"})
    return items


@require_http_methods(["GET", "POST"])
def api_gallery_items(request, gallery_id):
    gallery_id = _slugify(gallery_id)
    if request.method == "GET":
        items = _load_gallery_items(gallery_id)
        return JsonResponse({"items": items, "limit": WORKS_MAX_ITEMS}, status=200)

    # POST
    # On Vercel, request.user doesn't exist (no auth middleware)
    if not hasattr(request, 'user') or not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if _gallery_item_count(gallery_id) >= WORKS_MAX_ITEMS:
        return JsonResponse({"error": f"Limit reached ({WORKS_MAX_ITEMS} photos). Remove one to add another."}, status=409)

    title = request.POST.get("title", "").strip()
    image_file = request.FILES.get("image")
    thumb_file = request.FILES.get("thumbnail")

    errors = {}
    if not title:
        errors["title"] = "Title is required."
    if not image_file:
        errors["image"] = "Full image is required."
    if not thumb_file:
        errors["thumbnail"] = "Thumbnail image is required."

    def _valid(file_obj):
        return file_obj and Path(file_obj.name).suffix.lower() in IMAGE_EXTS

    if image_file and not _valid(image_file):
        errors["image"] = "Full image must be an image file."
    if thumb_file and not _valid(thumb_file):
        errors["thumbnail"] = "Thumbnail must be an image file."

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    item = _save_gallery_item(gallery_id, title, image_file, thumb_file)
    return JsonResponse({"item": item, "limit": WORKS_MAX_ITEMS}, status=201)


@require_http_methods(["DELETE"])
def api_gallery_item_detail(request, gallery_id, item_id):
    # On Vercel, request.user doesn't exist (no auth middleware)
    if not hasattr(request, 'user') or not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    _delete_gallery_item(gallery_id, item_id)
    return JsonResponse({"success": True})


# Project management views
def add_project(request):
    """Add a new project"""
    if not _ensure_staff(request):
        return redirect('works')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        uploaded_images = request.FILES.getlist('images')
        
        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        if not category:
            errors['category'] = 'Category is required.'
        if not uploaded_images:
            errors['images'] = 'At least one image is required.'
        
        # Validate image files
        for img in uploaded_images:
            if Path(img.name).suffix.lower() not in IMAGE_EXTS:
                errors['images'] = f'Invalid file type: {img.name}. Only image files are allowed.'
                break
        
        if not errors:
            projects = _load_projects()
            project_id = _slugify(title)
            
            # Check if ID already exists
            if any(p.get('id') == project_id for p in projects):
                errors['title'] = 'A project with this title already exists.'
            else:
                # Save uploaded images
                saved_filenames = []
                try:
                    for img_file in uploaded_images:
                        filename = _save_project_image(img_file)
                        saved_filenames.append(filename)
                    
                    new_project = {
                        "id": project_id,
                        "title": title.upper(),
                        "description": description,
                        "category": category,
                        "images": saved_filenames,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    projects.append(new_project)
                    _save_projects(projects)
                    messages.success(request, f'Project added successfully with {len(saved_filenames)} images!')
                    return redirect('works')
                except Exception as e:
                    errors['general'] = f'Error saving images: {str(e)}'
        
        if errors:
            for key, msg in errors.items():
                messages.error(request, msg)
    
    return render(request, 'add_project.html')


def edit_project(request, project_id):
    """Edit an existing project"""
    if not _ensure_staff(request):
        return redirect('works')
    
    project = _load_project(project_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        uploaded_images = request.FILES.getlist('new_images')
        keep_existing = request.POST.get('keep_existing', 'true') == 'true'
        
        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        if not category:
            errors['category'] = 'Category is required.'
        
        # Must have either existing images or upload new ones
        if not keep_existing and not uploaded_images:
            errors['images'] = 'At least one image is required.'
        
        # Validate uploaded image files
        for img in uploaded_images:
            if Path(img.name).suffix.lower() not in IMAGE_EXTS:
                errors['images'] = f'Invalid file type: {img.name}. Only image files are allowed.'
                break
        
        if not errors:
            # Save new uploaded images
            new_filenames = []
            try:
                for img_file in uploaded_images:
                    filename = _save_project_image(img_file)
                    new_filenames.append(filename)
                
                projects = _load_projects()
                for p in projects:
                    if p.get('id') == project_id:
                        p['title'] = title.upper()
                        p['description'] = description
                        p['category'] = category
                        # Keep existing images if checkbox is checked, otherwise replace with new ones
                        if keep_existing and new_filenames:
                            p['images'] = p.get('images', []) + new_filenames
                        elif new_filenames:
                            p['images'] = new_filenames
                        # If keeping existing and no new uploads, keep current images
                        break
                
                _save_projects(projects)
                if new_filenames:
                    messages.success(request, f'Project updated with {len(new_filenames)} new images!')
                else:
                    messages.success(request, 'Project updated successfully!')
                return redirect('works')
            except Exception as e:
                errors['general'] = f'Error saving images: {str(e)}'
        
        if errors:
            for key, msg in errors.items():
                messages.error(request, msg)
    
    return render(request, 'edit_project.html', {
        'project': project
    })


def delete_project(request, project_id):
    """Delete a project"""
    if not _ensure_staff(request):
        return redirect('works')
    
    if request.method == 'POST':
        projects = _load_projects()
        projects = [p for p in projects if p.get('id') != project_id]
        _save_projects(projects)
        messages.success(request, 'Project deleted successfully!')
    
    return redirect('works')

