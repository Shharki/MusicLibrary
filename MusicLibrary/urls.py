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
    # Home, search
    HomeView, search_suggestions,

    # Songs
    SongsListView, SongDetailView, SongCreateView, SongUpdateView, SongDeleteView,
    # Albums
    AlbumsListView, AlbumDetailView, AlbumCreateView, AlbumUpdateView, AlbumDeleteView, AlbumSongOrderUpdateView,

    # Contributors
    ContributorsListView, ContributorDetailView, ContributorCreateView, ContributorUpdateView, ContributorDeleteView,
    # Contributor role
    ContributorRolesListView, ContributorRoleDetailView, ContributorRoleCreateView, ContributorRoleUpdateView,
    ContributorRoleDeleteView,
    # Contributor song performance
    ContributorSongPerformanceCreateView, ContributorSongPerformanceUpdateView, ContributorSongPerformanceDeleteView,

    # Music groups
    MusicGroupsListView, MusicGroupDetailView, MusicGroupCreateView, MusicGroupUpdateView, MusicGroupDeleteView,
    # Music group role
    MusicGroupRolesListView, MusicGroupRoleDetailView,
    MusicGroupRoleCreateView, MusicGroupRoleUpdateView, MusicGroupRoleDeleteView,
    # Music group membership
    MusicGroupMembershipCreateView, MusicGroupMembershipUpdateView, MusicGroupMembershipDeleteView,

    # Countries
    CountriesListView, CountryDetailView, CountryCreateView, CountryUpdateView, CountryDeleteView,
    # Languages
    LanguagesListView, LanguageDetailView, LanguageCreateView, LanguageUpdateView, LanguageDeleteView,
    # Genres
    GenresListView, GenreDetailView, GenreCreateView, GenreUpdateView, GenreDeleteView,
    SongPerformanceContributorCreateView, SongPerformanceMusicGroupCreateView, SongPerformanceMusicGroupUpdateView,
    SongPerformanceMusicGroupDeleteView, SongPerformanceContributorDeleteView, SongPerformanceContributorUpdateView,
)

urlpatterns = [
    # Admin panel and accounts
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),

    # Home
    path('', HomeView.as_view(), name='home'),

    # Search field
    path("c/", search_suggestions, name="search_suggestions"),

    # Songs
    path('songs/', SongsListView.as_view(), name='songs'),
    path('song/<int:pk>/', SongDetailView.as_view(), name='song'),
    path('song/create/', SongCreateView.as_view(), name='song_create'),
    path('song/update/<int:pk>/', SongUpdateView.as_view(), name='song_update'),
    path('song/delete/<int:pk>/', SongDeleteView.as_view(), name='song_delete'),
    # Contributor performance URLs
    path('song-performance-contributor/create/', SongPerformanceContributorCreateView.as_view(), name='song_performance_contributor_create'),
    path('song-performance-contributor/<int:pk>/update/', SongPerformanceContributorUpdateView.as_view(), name='contributor_song_performance_update'),
    path('song-performance-contributor/<int:pk>/delete/', SongPerformanceContributorDeleteView.as_view(), name='contributor_song_performance_delete'),

    # Music group performance URLs
    path('song-performance-music-group/create/', SongPerformanceMusicGroupCreateView.as_view(), name='song_performance_music_group_create'),
    path('song-performance-music-group/<int:pk>/update/', SongPerformanceMusicGroupUpdateView.as_view(), name='music_group_performance_update'),
    path('song-performance-music-group/<int:pk>/delete/', SongPerformanceMusicGroupDeleteView.as_view(), name='music_group_performance_delete'),


    # Albums
    path('albums/', AlbumsListView.as_view(), name='albums'),
    path('album/<int:pk>/', AlbumDetailView.as_view(), name='album'),
    path('album/create/', AlbumCreateView.as_view(), name='album_create'),
    path('album/update/<int:pk>/', AlbumUpdateView.as_view(), name='album_update'),
    path('album/delete/<int:pk>/', AlbumDeleteView.as_view(), name='album_delete'),
    path('album/<int:album_pk>/song-order-update/', AlbumSongOrderUpdateView.as_view(), name='album_song_order_update'),

    # Contributors
    path('contributors/', ContributorsListView.as_view(), name='contributors'),
    path('contributor/<int:pk>/', ContributorDetailView.as_view(), name='contributor'),
    path('contributor/create/', ContributorCreateView.as_view(), name='contributor_create'),
    path('contributor/update/<int:pk>/', ContributorUpdateView.as_view(), name='contributor_update'),
    path('contributor/delete/<int:pk>/', ContributorDeleteView.as_view(), name='contributor_delete'),

    # Contributor role
    path('contributor-roles/', ContributorRolesListView.as_view(), name='contributor_roles'),
    path('contributor-role/<int:pk>/', ContributorRoleDetailView.as_view(), name='contributor_role'),
    path('contributor-role/create/', ContributorRoleCreateView.as_view(), name='contributor_role_create'),
    path('contributor-role/<int:pk>/edit/', ContributorRoleUpdateView.as_view(), name='contributor_role_update'),
    path('contributor-role/<int:pk>/delete/', ContributorRoleDeleteView.as_view(), name='contributor_role_delete'),

    # Contributor song performance
    path(
        'contributor-song-performance/<int:contributor_pk>/create/',
        ContributorSongPerformanceCreateView.as_view(),
        name='contributor_song_performance_create'),
    path(
        'contributor-song-performance/<int:pk>/edit/',
        ContributorSongPerformanceUpdateView.as_view(),
        name='contributor_song_performance_update'),
    path(
        'contributor-song-performance/<int:pk>/delete/',
        ContributorSongPerformanceDeleteView.as_view(),
        name='contributor_song_performance_delete'),

    # Music groups
    path('music-groups/', MusicGroupsListView.as_view(), name='music_groups'),
    path('music-group/<int:pk>/', MusicGroupDetailView.as_view(), name='music_group'),
    path('music-group/create/', MusicGroupCreateView.as_view(), name='music_group_create'),
    path('music-group/update/<int:pk>/', MusicGroupUpdateView.as_view(), name='music_group_update'),
    path('music-group/delete/<int:pk>/', MusicGroupDeleteView.as_view(), name='music_group_delete'),


    # Music group role
    path('music-group-roles/', MusicGroupRolesListView.as_view(), name='music_group_roles'),
    path('music-group-role/<int:pk>/', MusicGroupRoleDetailView.as_view(), name='music_group_role'),
    path('music-group-role/create/', MusicGroupRoleCreateView.as_view(), name='music_group_role_create'),
    path('music-group-role/<int:pk>/edit/', MusicGroupRoleUpdateView.as_view(), name='music_group_role_update'),
    path('music-group-role/<int:pk>/delete/', MusicGroupRoleDeleteView.as_view(), name='music_group_role_delete'),

    # Music group membership
    path('music-group-membership/<int:contributor_pk>/create/', MusicGroupMembershipCreateView.as_view(), name='music_group_membership_create'),
    path('music-group-membership/<int:pk>/edit/', MusicGroupMembershipUpdateView.as_view(), name='music_group_membership_update'),
    path('music-group-membership/<int:pk>/delete/', MusicGroupMembershipDeleteView.as_view(), name='music_group_membership_delete'),

    # Countries
    path('countries/', CountriesListView.as_view(), name='countries'),
    path('country/<int:pk>', CountryDetailView.as_view(), name='country'),
    path('country/create/', CountryCreateView.as_view(), name='country_create'),
    path('country/update/<int:pk>/', CountryUpdateView.as_view(), name='country_update'),
    path('country/delete/<int:pk>/', CountryDeleteView.as_view(), name='country_delete'),

    # Languages
    path('languages/', LanguagesListView.as_view(), name='languages'),
    path('language/<int:pk>', LanguageDetailView.as_view(), name='language'),
    path('language/create/', LanguageCreateView.as_view(), name='language_create'),
    path('language/update/<int:pk>/', LanguageUpdateView.as_view(), name='language_update'),
    path('language/delete/<int:pk>/', LanguageDeleteView.as_view(), name='language_delete'),

    # Genres
    path('genres/', GenresListView.as_view(), name='genres'),
    path('genre/<int:pk>', GenreDetailView.as_view(), name='genre'),
    path('genre/create/', GenreCreateView.as_view(), name='genre_create'),
    path('genre/update/<int:pk>/', GenreUpdateView.as_view(), name='genre_update'),
    path('genre/delete/<int:pk>/', GenreDeleteView.as_view(), name='genre_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)