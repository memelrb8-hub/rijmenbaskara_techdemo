from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='format_article_date')
def format_article_date(timestamp_str):
    """
    Convert timestamp string like '20251220165204' to '20 Dec'
    Format: j M (Day Month abbreviated)
    """
    if not timestamp_str:
        return ""
    
    try:
        # Parse timestamp format: YYYYMMDDHHmmss
        if len(timestamp_str) >= 8:
            year = int(timestamp_str[:4])
            month = int(timestamp_str[4:6])
            day = int(timestamp_str[6:8])
            dt = datetime(year, month, day)
            return dt.strftime("%d %b")  # e.g., "20 Dec"
    except (ValueError, IndexError):
        pass
    
    return timestamp_str[:8] if len(timestamp_str) >= 8 else timestamp_str


@register.filter(name='is_staff')
def is_staff(request):
    """
    Check if user is authenticated via session.
    """
    return request.session.get('is_authenticated', False)


@register.simple_tag(takes_context=True)
def admin_url(context, url_name, *args, **kwargs):
    """
    Generate URL (no longer needs to preserve admin parameter).
    Kept for compatibility but just returns normal URL.
    """
    from django.urls import reverse
    return reverse(url_name, args=args, kwargs=kwargs)
