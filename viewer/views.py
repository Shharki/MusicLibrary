import os

from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView

from viewer.models import (
    Song, MusicGroupMembership, Contributor, Album, SongPerformance, Genre, Language, MusicGroup, Country
)
from viewer.utils import format_seconds


class HomeView(ListView):
    model = Album
    template_name = 'home.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.exclude(cover_image='').exclude(cover_image__isnull=True).order_by('?')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        albums = context['albums']
        for index, album in enumerate(albums):
            file_path = os.path.join(settings.MEDIA_ROOT, album.cover_image.name)
            if os.path.exists(file_path):
                album.image_url = album.cover_image.url
            else:
                placeholder_number = (index % 6) + 1  # 1 až 6
                album.image_url = f"{settings.STATIC_URL}images/placeholders/placeholder{placeholder_number}.jpg"
        return context


class SongsListView(ListView):
    template_name = 'songs.html'
    model = Song
    context_object_name = 'songs'


class SongDetailView(DetailView):
    template_name = 'song.html'
    model = Song
    context_object_name = 'song'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song = self.object

        context.update({
            'contributors_by_category': song.contributors_by_category(),
            'groups_by_role': song.groups_by_role(),
            'album': song.first_album(),
            'song_artists': song.artists(),
            'song_music_groups': song.music_groups(),
        })
        return context


class ContributorsListView(TemplateView):
    template_name = 'contributors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['performers'] = Contributor.objects.filter(
            song_performances__contributor_role__category='performer'
        ).distinct()

        context['producers'] = Contributor.objects.filter(
            song_performances__contributor_role__category='producer'
        ).distinct()

        context['writers'] = Contributor.objects.filter(
            song_performances__contributor_role__category='writer'
        ).distinct()

        return context


class ContributorDetailView(DetailView):
    template_name = 'contributor.html'
    model = Contributor
    context_object_name = 'contributor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contributor = self.object

        songs = contributor.songs.all()  # Songs in which he participated
        albums = contributor.albums.all()  # Albums he has contributed to (optional)
        memberships = contributor.memberships.select_related('music_group').all()  # Group membership (optional)

        context.update({
            'songs': songs,
            'albums': albums,
            'memberships': memberships,
        })

        return context


class AlbumsListView(ListView):
    template_name = 'albums.html'
    model = Album
    context_object_name = 'albums'


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'album.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object

        songs = album.ordered_songs()
        genres = album.genres_list()
        languages = album.languages_list()
        contributors_by_category = album.contributors_by_category()
        groups_by_role = album.groups_by_role()

        genre_label = "Genre" if genres.count() == 1 else "Genres"
        language_label = "Language" if languages.count() == 1 else "Languages"

        context.update({
            'songs': songs,
            'total_duration': album.total_duration(),
            'genres': genres,
            'genre_label': genre_label,
            'languages': languages,
            'language_label': language_label,
            'contributors_by_category': contributors_by_category,
            'groups_by_role': groups_by_role,
            'album_artists': album.artist.all(),
            'album_music_groups': album.music_group.all(),
        })
        return context


class MusicGroupsListView(ListView):
    template_name = 'music-groups.html'
    model = MusicGroup
    context_object_name = 'music_groups'


class MusicGroupDetailView(DetailView):
    template_name = 'music-group.html'
    model = MusicGroup
    context_object_name = 'music_group'


class CountriesListView(ListView):
    template_name = 'countries.html'
    model = Country
    context_object_name = 'countries'


class CountryDetailView(DetailView):
    template_name = 'country.html'
    model = Country
    context_object_name = 'country'


class GenresListView(ListView):
    template_name = 'genres.html'
    model = Genre
    context_object_name ='genres'


class GenreDetailView(DetailView):
    template_name = 'genre.html'
    model = Genre
    context_object_name = 'genre'

