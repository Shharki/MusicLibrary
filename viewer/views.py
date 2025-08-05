import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from viewer.forms import (
    GenreModelForm, CountryModelForm, ContributorModelForm, MusicGroupModelForm, SongModelForm, AlbumModelForm
)
from viewer.models import (
    Song, Contributor, Album, Genre, Country, AlbumSong, MusicGroup,
)


class HomeView(ListView):
    model = Album
    template_name = 'home.html'
    context_object_name = 'albums'
    login_url = 'login'

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


# Song Views
class SongsListView(ListView):
    model = Song
    template_name = 'songs.html'
    context_object_name = 'songs'
    paginate_by = 10

    def get_ordering(self):
        order = self.request.GET.get('order', 'asc')
        return 'title' if order == 'asc' else '-title'

    def get_paginate_by(self, queryset):
        try:
            return int(self.request.GET.get('paginate_by', self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by

    def get_queryset(self):
        queryset = super().get_queryset()
        order = self.request.GET.get("order", "asc")
        letter = self.request.GET.get("letter")

        if letter:
            queryset = queryset.filter(title__istartswith=letter)

        if order == "desc":
            queryset = queryset.order_by("-title")
        else:
            queryset = queryset.order_by("title")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paginate_options'] = [10, 20, 50, 100]
        context['alphabet'] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return context

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


class SongCreateView(CreateView):
    template_name = 'form.html'
    form_class = SongModelForm
    success_url = reverse_lazy('songs')


class SongUpdateView(UpdateView):
    template_name = 'form.html'
    form_class = SongModelForm
    model = Song
    success_url = reverse_lazy('songs')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class SongDeleteView(DeleteView):
    template_name = 'confirm_delete.html'
    model = Song
    success_url = reverse_lazy('songs')


# Contributor Views
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

        context['publishers'] = Contributor.objects.filter(
            song_performances__contributor_role__category='publisher'
        ).distinct()

        context['others'] = Contributor.objects.filter(
            song_performances__contributor_role__category='other'
        ).distinct()

        context['without_role'] = Contributor.objects.exclude(
            Q(song_performances__isnull=False)
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
            'songs_by_category': contributor.songs_grouped_by_category(),
        })

        return context


class ContributorCreateView(CreateView):
    template_name = 'form.html'
    form_class = ContributorModelForm
    success_url = reverse_lazy('contributors')


class ContributorUpdateView(UpdateView):
    template_name = 'form.html'
    form_class = ContributorModelForm
    model = Contributor
    success_url = reverse_lazy('contributors')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class ContributorDeleteView(DeleteView):
    template_name = 'confirm_delete.html'
    model = Contributor
    success_url = reverse_lazy('contributors')


# Album Views
class AlbumsListView(ListView):
    model = Album
    template_name = 'albums.html'
    context_object_name = 'albums'
    paginate_by = 10

    def get_ordering(self):
        order = self.request.GET.get('order', 'asc')
        return 'title' if order == 'asc' else '-title'

    def get_paginate_by(self, queryset):
        try:
            return int(self.request.GET.get('paginate_by', self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by

    def get_queryset(self):
        queryset = super().get_queryset()
        letter = self.request.GET.get("letter")

        if letter:
            queryset = queryset.filter(title__istartswith=letter)

        return queryset.order_by(self.get_ordering())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paginate_options'] = [10, 20, 50, 100]
        context['alphabet'] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return context


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'album.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object

        # Vezmeme AlbumSong queryset, abychom měli order i song
        album_songs = AlbumSong.objects.filter(album=album).select_related('song').order_by('order')

        genres = album.genres_list()
        languages = album.languages_list()
        contributors_by_category = album.contributors_by_category()
        groups_by_role = album.groups_by_role()

        genre_label = "Genre" if genres.count() == 1 else "Genres"
        language_label = "Language" if languages.count() == 1 else "Languages"

        context.update({
            'album_songs': album_songs,   # Objekt AlbumSong obsahuje song i order
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


class AlbumCreateView(CreateView):
    model = Album
    form_class = AlbumModelForm
    template_name = 'form.html'
    success_url = reverse_lazy('albums')

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Zpracování obrázku (pokud byl nahrán)
        if self.request.FILES.get('cover_image'):
            self.object.cover_image = self.request.FILES['cover_image']

        self.object.save()
        form.save_m2m()  # uloží artist, music_group, songs (form.cleaned_data)

        songs = form.cleaned_data.get('songs', [])
        if not songs:
            form.add_error('songs', 'At least one song must be selected.')
            return self.form_invalid(form)

        # Smažeme existující vazby pro případ opakovaného použití view
        AlbumSong.objects.filter(album=self.object).delete()

        # Vytvoření AlbumSong vazeb s pořadím
        for index, song in enumerate(songs, start=1):
            AlbumSong.objects.create(
                album=self.object,
                song=song,
                order=index
            )

        return redirect(self.get_success_url())


class AlbumUpdateView(UpdateView):
    model = Album
    form_class = AlbumModelForm
    template_name = 'form.html'
    success_url = reverse_lazy('albums')

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.request.FILES.get('cover_image'):
            self.object.cover_image = self.request.FILES['cover_image']

        self.object.save()
        form.save_m2m()

        songs = form.cleaned_data.get('songs', [])
        if not songs:
            form.add_error('songs', 'At least one song must be selected.')
            return self.form_invalid(form)

        AlbumSong.objects.filter(album=self.object).delete()

        for index, song in enumerate(songs, start=1):
            AlbumSong.objects.create(
                album=self.object,
                song=song,
                order=index
            )

        return redirect(self.get_success_url())


class AlbumDeleteView(DeleteView):
    model = Album
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('albums')


# Music Group Views
from django.views.generic import ListView
from .models import MusicGroup  # uprav podle své appky a modelu

class MusicGroupsListView(ListView):
    model = MusicGroup
    template_name = 'music-groups.html'
    context_object_name = 'music_groups'
    paginate_by = 10

    def get_ordering(self):
        order = self.request.GET.get('order', 'asc')
        return 'name' if order == 'asc' else '-name'

    def get_paginate_by(self, queryset):
        try:
            return int(self.request.GET.get('paginate_by', self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by

    def get_queryset(self):
        queryset = super().get_queryset()
        letter = self.request.GET.get('letter')

        if letter:
            queryset = queryset.filter(name__istartswith=letter)

        return queryset.order_by(self.get_ordering())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paginate_options'] = [10, 20, 50, 100]
        context['alphabet'] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return context



class MusicGroupDetailView(DetailView):
    template_name = 'music-group.html'
    model = MusicGroup
    context_object_name = 'music_group'


class MusicGroupCreateView(CreateView):
    template_name = 'form.html'
    form_class = MusicGroupModelForm
    success_url = reverse_lazy('music-groups')


class MusicGroupUpdateView(UpdateView):
    template_name = 'form.html'
    form_class = MusicGroupModelForm
    model = MusicGroup
    success_url = reverse_lazy('music-groups')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class MusicGroupDeleteView(DeleteView):
    template_name = 'confirm_delete.html'
    model = MusicGroup
    success_url = reverse_lazy('music-groups')


# Country Views
class CountriesListView(LoginRequiredMixin, ListView):
    template_name = 'countries.html'
    model = Country
    context_object_name = 'countries'


class CountryDetailView(LoginRequiredMixin, DetailView):
    template_name = 'country.html'
    model = Country
    context_object_name = 'country'


class CountryCreateView(CreateView):
    template_name = 'form.html'
    form_class = CountryModelForm
    success_url = reverse_lazy('countries')


class CountryUpdateView(UpdateView):
    template_name = 'form.html'
    form_class = CountryModelForm
    model = Country
    success_url = reverse_lazy('countries')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class CountryDeleteView(DeleteView):
    template_name = 'confirm_delete.html'
    model = Country
    success_url = reverse_lazy('countries')


# Genre Views
class GenresListView(LoginRequiredMixin, ListView):
    template_name = 'genres.html'
    model = Genre
    context_object_name ='genres'


class GenreDetailView(LoginRequiredMixin, DetailView):
    template_name = 'genre.html'
    model = Genre
    context_object_name = 'genre'


class GenreCreateView(CreateView):
    template_name = 'form.html'  # Reusable form template
    form_class = GenreModelForm     # Use custom form with validation
    success_url = reverse_lazy('genres')  # Redirect after success

    # form_valid is not needed --> CreateView handles saving


class GenreUpdateView(UpdateView):
    template_name = 'form.html'
    form_class = GenreModelForm
    model = Genre
    success_url = reverse_lazy('genres')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class GenreDeleteView(DeleteView):
    template_name = 'confirm_delete.html'
    model = Genre
    success_url = reverse_lazy('genres')


@require_POST
def album_song_order_update(request, album_pk):
    album = get_object_or_404(Album, pk=album_pk)

    # Načteme všechny AlbumSong záznamy pro dané album
    album_songs = list(AlbumSong.objects.filter(album=album))

    # Počet písní v albu
    max_order = len(album_songs)

    # Slovník song_id -> new_order z POST
    new_orders = {}

    # Pro sběr chyb
    errors = []

    # Načteme a validujeme všechny ordery z POST dat
    for album_song in album_songs:
        field_name = f'order_{album_song.song.pk}'
        value = request.POST.get(field_name)

        if value is None:
            errors.append(f"Missing order for song '{album_song.song.title}'.")
            continue

        try:
            order_num = int(value)
            if order_num < 1 or order_num > max_order:
                errors.append(f"Order for song '{album_song.song.title}' must be between 1 and {max_order}.")
                continue
            new_orders[album_song.song.pk] = order_num
        except ValueError:
            errors.append(f"Invalid order value for song '{album_song.song.title}'.")

    # Zkontrolujeme duplicity mezi novými pořadími
    orders_list = list(new_orders.values())
    if len(orders_list) != len(set(orders_list)):
        errors.append("Duplicate order numbers are not allowed.")

    # Pokud máme chyby, zobrazíme je uživateli a neprovedeme změny
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect('album', pk=album.pk)

    # Pokud validace prošla, uložíme změny atomicky
    with transaction.atomic():
        for album_song in album_songs:
            new_order = new_orders.get(album_song.song.pk)
            if new_order is not None and new_order != album_song.order:
                album_song.order = new_order
                album_song.save()

    messages.success(request, "Song order updated successfully.")
    return redirect('album', pk=album.pk)
