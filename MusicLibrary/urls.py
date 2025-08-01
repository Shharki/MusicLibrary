"""
URL configuration for MusicLibrary project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from viewer.views import (
    SongsListView, SongDetailView, ContributorsListView, ContributorDetailView, AlbumsListView, AlbumDetailView, \
    MusicGroupsListView, MusicGroupDetailView, CountriesListView, HomeView
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('songs/', SongsListView.as_view(), name='songs'),
    path('song/<int:pk>/', SongDetailView.as_view(), name='song'),
    path('contributors/', ContributorsListView.as_view(), name='contributors'),
    path('contributor/<int:pk>/', ContributorDetailView.as_view(), name='contributor'),
    path('albums/', AlbumsListView.as_view(), name='albums'),
    path('album/<int:pk>/', AlbumDetailView.as_view(), name='album'),
    path('music-groups/', MusicGroupsListView.as_view(), name='music-groups'),
    path('music-group/<int:pk>/', MusicGroupDetailView.as_view(), name='music-group'),
    path('countries/', CountriesListView.as_view(), name='countries'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)