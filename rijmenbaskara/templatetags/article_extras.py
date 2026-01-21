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
    Check if viewing in admin mode.
    Priority: 1) Real authentication 2) URL parameter fallback for POC
    """
    # Check real authentication first
    if hasattr(request, 'user') and hasattr(request.user, 'is_authenticated'):
        if request.user.is_authenticated and hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True
    
    # Fallback to URL parameter for POC mode
    if hasattr(request, 'GET') and request.GET.get('admin') == 'true':
        return True
    
    return False


@register.simple_tag(takes_context=True)
def admin_url(context, url_name, *args, **kwargs):
    """
    Generate URL that preserves admin mode parameter.
    Usage: {% admin_url 'view_name' %} or {% admin_url 'view_name' arg1 arg2 %}
    """
    from django.urls import reverse
    request = context.get('request')
    url = reverse(url_name, args=args, kwargs=kwargs)
    
    # If currently in admin mode, append the parameter
    if request and hasattr(request, 'GET') and request.GET.get('admin') == 'true':
        url += '?admin=true'
    
    return url
