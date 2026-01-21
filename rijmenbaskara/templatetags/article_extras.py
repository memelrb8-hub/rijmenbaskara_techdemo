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
    Check if viewing in admin mode (POC: uses URL parameter).
    Falls back to actual auth if available.
    """
    # For Vercel POC: check URL parameter for admin mode
    if hasattr(request, 'GET') and request.GET.get('admin') == 'true':
        return True
    # Fallback to actual authentication
    return hasattr(request, 'user') and hasattr(request.user, 'is_staff') and request.user.is_staff
