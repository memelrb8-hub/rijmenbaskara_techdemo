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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('works/', views.works, name='works'),
    path('articles/', views.articles, name='articles'),
    path('articles/new/', views.add_article, name='add_article'),
    path('articles/manage/', views.manage_articles, name='manage_articles'),
    path('articles/<slug:article_id>/edit/', views.edit_article, name='edit_article'),
    path('articles/<slug:article_id>/', views.article_detail, name='article_detail'),
    path('about/', views.about, name='about'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
