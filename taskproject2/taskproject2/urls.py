"""taskproject2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.utils import delete_item
from invitations.functions import activate_invite

from .views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('activate/invitation/<str:uidb64>/<str:token>/', activate_invite, name='activate-invite'),
    path('projects/', include('projects.urls',namespace='projects')),
    path('companies/', include('companies.urls',namespace='companies')),
    path('invitations/', include('invitations.urls',namespace='invitations')),
    path('delete/', delete_item, name='delete'),
    path('users/', include('users.urls')),
    path('users/api/', include('users.api.routers')),
    path('profiles/', include('profiles.urls')),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
