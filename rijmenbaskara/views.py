from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from pathlib import Path
import json
import re
from datetime import datetime

# File-based article storage (local file management)
ARTICLES_DIR = Path(settings.BASE_DIR) / "articles_store"
ARTICLES_DIR.mkdir(exist_ok=True)
ARTICLES_COVERS_DIR = ARTICLES_DIR / "covers"
ARTICLES_COVERS_DIR.mkdir(exist_ok=True)


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


def _ensure_staff(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Admins only.")
        return False
    return True

# Preset tags
TAG_CHOICES = [
    "Armor", "Aircraft", "Ship", "Automotive", "Figure",
    "Tutorial", "Review", "Diorama", "WIP", "Finished"
]

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
    return render(request, 'home.html')

def works(request):
    return render(request, 'works.html')

def articles(request):
    items = _load_articles()
    active_tag = request.GET.get('tag', '').strip()
    if active_tag:
        items = [a for a in items if active_tag in (a.get("tags") or [])]

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
    })

def about(request):
    return render(request, 'about.html')


def article_detail(request, article_id):
    article = _load_article(article_id)
    return render(request, 'article_detail.html', {"article": article})

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

            _article_path(article_id).write_text(
                json.dumps(record, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            messages.success(
                request,
                'Draft saved locally.' if is_edit else 'Draft created locally.'
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
