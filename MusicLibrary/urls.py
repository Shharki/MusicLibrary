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
from django.urls import path, include

from viewer.views import (
    HomeView,
    # Songs
    SongsListView, SongDetailView, SongCreateView, SongUpdateView, SongDeleteView,
    # Contributors
    ContributorsListView, ContributorDetailView, ContributorCreateView, ContributorUpdateView, ContributorDeleteView,
    # Albums
    AlbumsListView, AlbumDetailView, AlbumCreateView, AlbumUpdateView, AlbumDeleteView,
    # Music Groups
    MusicGroupsListView, MusicGroupDetailView, MusicGroupCreateView, MusicGroupUpdateView, MusicGroupDeleteView,
    # Countries
    CountriesListView, CountryDetailView, CountryCreateView, CountryUpdateView, CountryDeleteView,
    # Genres
    GenresListView, GenreDetailView, GenreCreateView, GenreUpdateView, GenreDeleteView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', HomeView.as_view(), name='home'),

    # Songs
    path('songs/', SongsListView.as_view(), name='songs'),
    path('song/<int:pk>/', SongDetailView.as_view(), name='song'),
    path('song/create/', SongCreateView.as_view(), name='song_create'),
    path('song/update/<int:pk>/', SongUpdateView.as_view(), name='song_update'),
    path('song/delete/<int:pk>/', SongDeleteView.as_view(), name='song_delete'),

    # Contributors
    path('contributors/', ContributorsListView.as_view(), name='contributors'),
    path('contributor/<int:pk>/', ContributorDetailView.as_view(), name='contributor'),
    path('contributor/create/', ContributorCreateView.as_view(), name='contributor_create'),
    path('contributor/update/<int:pk>/', ContributorUpdateView.as_view(), name='contributor_update'),
    path('contributor/delete/<int:pk>/', ContributorDeleteView.as_view(), name='contributor_delete'),

    # Albums
    path('albums/', AlbumsListView.as_view(), name='albums'),
    path('album/<int:pk>/', AlbumDetailView.as_view(), name='album'),
    path('album/create/', AlbumCreateView.as_view(), name='album_create'),
    path('album/update/<int:pk>/', AlbumUpdateView.as_view(), name='album_update'),
    path('album/delete/<int:pk>/', AlbumDeleteView.as_view(), name='album_delete'),

    # Music Groups
    path('music-groups/', MusicGroupsListView.as_view(), name='music-groups'),
    path('music-group/<int:pk>/', MusicGroupDetailView.as_view(), name='music-group'),
    path('music-group/create/', MusicGroupCreateView.as_view(), name='music-group_create'),
    path('music-group/update/<int:pk>/', MusicGroupUpdateView.as_view(), name='music-group_update'),
    path('music-group/delete/<int:pk>/', MusicGroupDeleteView.as_view(), name='music-group_delete'),

    # Countries
    path('countries/', CountriesListView.as_view(), name='countries'),
    path('country/<int:pk>', CountryDetailView.as_view(), name='country'),
    path('country/create/', CountryCreateView.as_view(), name='country_create'),
    path('country/update/<int:pk>/', CountryUpdateView.as_view(), name='country_update'),
    path('country/delete/<int:pk>/', CountryDeleteView.as_view(), name='country_delete'),

    # Genres
    path('genres/', GenresListView.as_view(), name='genres'),
    path('genre/<int:pk>', GenreDetailView.as_view(), name='genre'),
    path('genre/create/', GenreCreateView.as_view(), name='genre_create'),
    path('genre/update/<int:pk>/', GenreUpdateView.as_view(), name='genre_update'),
    path('genre/delete/<int:pk>/', GenreDeleteView.as_view(), name='genre_delete'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)