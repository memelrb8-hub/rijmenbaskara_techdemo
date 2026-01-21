"""
URL configuration for rijmenbaskara project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('works/', views.works, name='works'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/<slug:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/<slug:project_id>/delete/', views.delete_project, name='delete_project'),
    path('works/<slug:gallery_id>/add/', views.add_work, name='add_work'),
    path('api/galleries/<slug:gallery_id>/items/', views.api_gallery_items, name='api_gallery_items'),
    path('api/galleries/<slug:gallery_id>/items/<slug:item_id>/', views.api_gallery_item_detail, name='api_gallery_item_detail'),
    path('articles/', views.articles, name='articles'),
    path('articles/new/', views.add_article, name='add_article'),
    path('articles/manage/', views.manage_articles, name='manage_articles'),
    path('articles/export-backup/', views.export_content_backup, name='export_content_backup'),
    path('articles/<slug:article_id>/edit/', views.edit_article, name='edit_article'),
    path('articles/<slug:article_id>/', views.article_detail, name='article_detail'),
    path('about/', views.about, name='about'),
]

# Include admin URL (now works on Vercel with cookie-based sessions)
from django.contrib import admin
urlpatterns.insert(0, path('admin/', admin.site.urls))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
