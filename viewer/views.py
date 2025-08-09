import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from mixins import AlphabetOrderPaginationMixin, AlphabetOrderPaginationRelatedMixin, ContributorsByCategoryMixin, \
    SongPerformanceBaseMixin
from viewer.forms import (
    GenreModelForm, CountryModelForm, ContributorModelForm, MusicGroupModelForm, SongModelForm, AlbumModelForm,
    ContributorSongPerformanceForm, MusicGroupMembershipForm, LanguageModelForm, MusicGroupPerformanceForm,
    SongPerformanceContributorForm, SongPerformanceMusicGroupForm
)
from viewer.models import (
    Song, Contributor, Album, Genre, Country, AlbumSong, MusicGroup, ContributorRole, MusicGroupMembership,
    SongPerformance, MusicGroupRole, Language,
)

# Home
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
class SongsListView(AlphabetOrderPaginationMixin, ListView):
    model = Song
    template_name = 'songs.html'
    context_object_name = 'songs'
    default_paginate_by = 10
    default_order_field = 'title'

from collections import defaultdict, OrderedDict


from collections import OrderedDict
from django.views.generic import DetailView

from viewer.models import SongPerformance, Song

from collections import OrderedDict
from django.views.generic import DetailView
from viewer.models import SongPerformance, Song  # uprav podle skutečné cesty

class SongDetailView(DetailView):
    model = Song
    template_name = 'song.html'  # uprav podle potřeby

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song = self.object

        # Contributor performances (rozdělené podle contributor_role.category)
        contributor_performances = SongPerformance.objects.filter(
            song=song,
            contributor__isnull=False
        ).select_related('contributor', 'contributor_role')

        performances_by_category = OrderedDict()
        for perf in contributor_performances:
            category = perf.contributor_role.category if perf.contributor_role else 'other'
            if category not in performances_by_category:
                performances_by_category[category] = []
            performances_by_category[category].append(perf)

        # Music group performances (všechny do jednoho klíče "Music Groups")
        music_group_performances = SongPerformance.objects.filter(
            song=song,
            music_group__isnull=False
        ).select_related('music_group', 'music_group_role')

        # Všechny music group performances seskupíme pod jediný klíč
        performances_by_role = OrderedDict()
        performances_by_role['music_groups'] = list(music_group_performances)

        context['performances_by_category'] = performances_by_category
        context['music_group_performances_by_role'] = performances_by_role

        return context




class SongCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = SongModelForm
    success_url = reverse_lazy('songs')


class SongUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = SongModelForm
    model = Song
    success_url = reverse_lazy('songs')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class SongDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Song
    success_url = reverse_lazy('songs')


class SongPerformanceContributorCreateView(SongPerformanceBaseMixin, CreateView):
    form_class = SongPerformanceContributorForm


class SongPerformanceContributorUpdateView(UpdateView):
    model = SongPerformance
    form_class = SongPerformanceContributorForm
    template_name = "form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Předáme song do formuláře
        kwargs['song'] = self.object.song
        return kwargs

    def get_success_url(self):
        return reverse('song', kwargs={'pk': self.object.song.pk})


class SongPerformanceContributorDeleteView(DeleteView):
    model = SongPerformance
    template_name = "confirm_delete.html"

    def get_success_url(self):
        song = self.object.song
        return reverse('song', kwargs={'pk': song.pk})


class SongPerformanceMusicGroupCreateView(SongPerformanceBaseMixin, CreateView):
    form_class = SongPerformanceMusicGroupForm


class SongPerformanceMusicGroupUpdateView(UpdateView):
    model = SongPerformance
    form_class = SongPerformanceMusicGroupForm
    template_name = "form.html"

    def get_success_url(self):
        song = self.object.song
        return reverse('song', kwargs={'pk': song.pk})


class SongPerformanceMusicGroupDeleteView(DeleteView):
    model = SongPerformance
    template_name = "confirm_delete.html"

    def get_success_url(self):
        song = self.object.song
        return reverse('song', kwargs={'pk': song.pk})


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


class AlbumCreateView(LoginRequiredMixin, CreateView):
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


class AlbumUpdateView(LoginRequiredMixin, UpdateView):
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


class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = Album
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('albums')


class AlbumSongOrderUpdateView(LoginRequiredMixin, View):

    @method_decorator(require_POST)
    def post(self, request, album_pk):
        album = get_object_or_404(Album, pk=album_pk)
        album_songs = list(AlbumSong.objects.filter(album=album))
        max_order = len(album_songs)

        new_orders = {}
        errors = []

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

        orders_list = list(new_orders.values())
        if len(orders_list) != len(set(orders_list)):
            errors.append("Duplicate order numbers are not allowed.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('album', pk=album.pk)

        with transaction.atomic():
            for album_song in album_songs:
                new_order = new_orders.get(album_song.song.pk)
                if new_order is not None and new_order != album_song.order:
                    album_song.order = new_order
                    album_song.save()

        messages.success(request, "Song order updated successfully.")
        return redirect('album', pk=album.pk)


# Contributor Views
class ContributorsListView(TemplateView):
    template_name = 'contributors.html'
    paginate_per_column = 5  # výchozí počet položek na sloupec

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        letter = self.request.GET.get('letter')

        # Zkus načíst počet položek na sloupec z GET parametru
        try:
            self.paginate_per_column = int(self.request.GET.get('paginate_per_column', self.paginate_per_column))
        except (ValueError, TypeError):
            pass  # když je hodnota špatná, použij výchozí

        def get_paginated_contributors(category, page_param):
            qs = Contributor.objects.all().prefetch_related('song_performances__contributor_role')
            if category == 'without_role':
                qs = qs.exclude(song_performances__isnull=False)
            else:
                qs = qs.filter(song_performances__contributor_role__category=category)

            if letter:
                qs = qs.filter(
                    Q(first_name__istartswith=letter) |
                    Q(last_name__istartswith=letter) |
                    Q(stage_name__istartswith=letter)
                )

            qs = qs.distinct().order_by('last_name', 'first_name')

            paginator = Paginator(qs, self.paginate_per_column)
            page_number = self.request.GET.get(page_param)
            page_obj = paginator.get_page(page_number)

            # Přidej ke každému contributorovi atribut role_names jako string s jejich rolemi
            for contributor in page_obj.object_list:
                roles = contributor.song_performances.values_list('contributor_role__name', flat=True).distinct()
                contributor.role_names = ', '.join(sorted(set(roles))) if roles else '—'

            return page_obj, paginator

        performers_page_obj, performers_paginator = get_paginated_contributors('performer', 'page_performer')
        producers_page_obj, producers_paginator = get_paginated_contributors('producer', 'page_producer')
        writers_page_obj, writers_paginator = get_paginated_contributors('writer', 'page_writer')
        publishers_page_obj, publishers_paginator = get_paginated_contributors('publisher', 'page_publisher')
        others_page_obj, others_paginator = get_paginated_contributors('other', 'page_other')
        without_role_page_obj, without_role_paginator = get_paginated_contributors('without_role', 'page_without_role')

        context.update({
            'letter': letter,
            'alphabet': list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            'paginate_per_column': self.paginate_per_column,
            'pagination_options': [5, 10, 20],

            'performers': performers_page_obj.object_list,
            'performers_page_obj': performers_page_obj,
            'performers_paginator': performers_paginator,

            'producers': producers_page_obj.object_list,
            'producers_page_obj': producers_page_obj,
            'producers_paginator': producers_paginator,

            'writers': writers_page_obj.object_list,
            'writers_page_obj': writers_page_obj,
            'writers_paginator': writers_paginator,

            'publishers': publishers_page_obj.object_list,
            'publishers_page_obj': publishers_page_obj,
            'publishers_paginator': publishers_paginator,

            'others': others_page_obj.object_list,
            'others_page_obj': others_page_obj,
            'others_paginator': others_paginator,

            'without_role': without_role_page_obj.object_list,
            'without_role_page_obj': without_role_page_obj,
            'without_role_paginator': without_role_paginator,
        })

        return context



class ContributorDetailView(DetailView):
    template_name = 'contributor.html'
    model = Contributor
    context_object_name = 'contributor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contributor = self.object

        # SongPerformances pro daného contributora, eager load pro role a song
        song_performances = SongPerformance.objects.filter(contributor=contributor).select_related('song', 'contributor_role')

        # Seskupit podle role.category, hodnoty budou SongPerformance instance
        songs_by_category = {}
        for perf in song_performances:
            category = perf.contributor_role.category if perf.contributor_role else 'other'
            songs_by_category.setdefault(category, []).append(perf)

        # Ostatní data (můžeš zachovat)
        songs = contributor.songs.all()
        albums = contributor.albums.all()
        memberships = contributor.memberships.select_related('music_group').all()

        context.update({
            'songs': songs,
            'albums': albums,
            'memberships': memberships,
            'songs_by_category': songs_by_category,
            'song_performances': song_performances,
        })

        return context


class ContributorCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = ContributorModelForm
    success_url = reverse_lazy('contributors')


class ContributorUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = ContributorModelForm
    model = Contributor
    success_url = reverse_lazy('contributors')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class ContributorDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Contributor
    success_url = reverse_lazy('contributors')


# Contributor role
class ContributorRolesListView(AlphabetOrderPaginationMixin, ListView):
    model = ContributorRole
    template_name = 'contributor-roles.html'
    context_object_name = 'contributor_roles'
    default_order_field = 'name'
    paginate_options = [10, 20, 50, 100]
    default_paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        # přidáme anotaci počtu unikátních contributorů, kteří mají danou roli přes SongPerformance
        qs = qs.annotate(contributors_count=Count('songperformance__contributor', distinct=True))
        return qs


class ContributorRoleDetailView(AlphabetOrderPaginationRelatedMixin, DetailView):
    model = ContributorRole
    template_name = 'contributor-role.html'
    context_object_name = 'contributor_role'
    default_order_field = 'last_name'  # budeme řadit contributory podle jména

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Získáme contributory, kteří mají v nějakém SongPerformance tuto roli
        contributors_qs = Contributor.objects.filter(
            song_performances__contributor_role=self.object
        ).distinct()

        # Použijeme mixin k stránkování, řazení, filtrování podle abecedy
        page_obj = self.filter_order_paginate_queryset(contributors_qs)

        context['page_obj'] = page_obj
        context['paginate_options'] = self.paginate_options
        context['alphabet'] = self.get_alphabet()

        return context


class ContributorRoleCreateView(CreateView):
    model = ContributorRole
    fields = ['name', 'category']
    success_url = reverse_lazy('contributor_roles')
    template_name = 'form.html'


class ContributorRoleUpdateView(UpdateView):
    model = ContributorRole
    fields = ['name', 'category']
    success_url = reverse_lazy('roles')
    template_name = 'form.html'


class ContributorRoleDeleteView(DeleteView):
    model = ContributorRole
    success_url = reverse_lazy('roles')
    template_name = 'confirm_delete.html'


# Contributor song performance
class ContributorSongPerformanceCreateView(CreateView):
    model = SongPerformance
    form_class = ContributorSongPerformanceForm
    template_name = 'form.html'

    def get_initial(self):
        # Předvyplníme contributor do formuláře (např. hidden field nebo readonly)
        initial = super().get_initial()
        initial['contributor'] = self.kwargs['contributor_pk']
        return initial

    def get_success_url(self):
        return reverse('contributor', kwargs={'pk': self.kwargs['contributor_pk']})

    def form_valid(self, form):
        # Ujistíme se, že contributor bude vždy ten správný z URL,
        # a ne něco, co by mohl uživatel odeslat v POSTu
        contributor_pk = self.kwargs['contributor_pk']
        contributor = Contributor.objects.get(pk=contributor_pk)
        form.instance.contributor = contributor
        return super().form_valid(form)


class ContributorSongPerformanceUpdateView(UpdateView):
    model = SongPerformance
    form_class = ContributorSongPerformanceForm
    template_name = 'form.html'
    success_url = reverse_lazy('contributors')


class ContributorSongPerformanceDeleteView(DeleteView):
    model = SongPerformance
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('contributors')


# Music groups
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
            letter = letter.strip()

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


class MusicGroupCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = MusicGroupModelForm
    success_url = reverse_lazy('music_groups')


class MusicGroupUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = MusicGroupModelForm
    model = MusicGroup
    success_url = reverse_lazy('music_groups')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class MusicGroupDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = MusicGroup
    success_url = reverse_lazy('music_groups')


# Music group membership
class MusicGroupMembershipCreateView(CreateView):
    model = MusicGroupMembership
    form_class = MusicGroupMembershipForm
    template_name = 'form.html'

    def get_success_url(self):
        return reverse_lazy('contributor', kwargs={'pk': self.object.member.pk})

    def form_valid(self, form):
        contributor_pk = self.kwargs['contributor_pk']
        contributor = Contributor.objects.get(pk=contributor_pk)
        form.instance.member = contributor  # nastavím member přímo
        return super().form_valid(form)


class MusicGroupMembershipUpdateView(UpdateView):
    model = MusicGroupMembership
    form_class = MusicGroupMembershipForm
    template_name = 'form.html'

    def get_success_url(self):
        return reverse_lazy('contributor', kwargs={'pk': self.object.member.pk})


class MusicGroupMembershipDeleteView(DeleteView):
    model = MusicGroupMembership
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('contributor', kwargs={'pk': self.object.member.pk})


# Music group roles
class MusicGroupRolesListView(AlphabetOrderPaginationMixin, ListView):
    model = MusicGroupRole
    template_name = 'music-group-roles.html'
    context_object_name = 'page_obj'
    default_order_field = 'name'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        # Přidej groups_count = počet unikátních music groups, které mají danou roli přes songperformances
        qs = qs.annotate(
            groups_count=Count(
                'songperformance__music_group',
                distinct=True
            )
        )
        return qs


class MusicGroupRoleDetailView(DetailView):
    model = MusicGroupRole
    template_name = "music-group-role.html"
    context_object_name = "music_group_role"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.object
        performances = role.songperformance_set.select_related('music_group').all()
        music_groups = {p.music_group for p in performances if p.music_group is not None}
        context['music_groups'] = sorted(music_groups, key=lambda g: g.name)
        return context


class MusicGroupRoleCreateView(CreateView):
    model = MusicGroupRole
    fields = ['name']
    success_url = reverse_lazy('music_group_roles')
    template_name = 'form.html'

class MusicGroupRoleUpdateView(UpdateView):
    model = MusicGroupRole
    fields = ['name']
    success_url = reverse_lazy('music_group_roles')
    template_name = 'form.html'

class MusicGroupRoleDeleteView(DeleteView):
    model = MusicGroupRole
    success_url = reverse_lazy('music_group_roles')
    template_name = 'confirm_delete.html'


# Country Views
class CountriesListView(AlphabetOrderPaginationMixin, ListView):
    model = Country
    template_name = 'countries.html'
    context_object_name = 'countries'
    default_order_field = 'name'  # Uprav podle názvu pole ve tvém modelu Country
    default_paginate_by = 10


class CountryDetailView(LoginRequiredMixin, DetailView):
    template_name = 'country.html'
    model = Country
    context_object_name = 'country'


class CountryCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = CountryModelForm
    success_url = reverse_lazy('countries')


class CountryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = CountryModelForm
    model = Country
    success_url = reverse_lazy('countries')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class CountryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Country
    success_url = reverse_lazy('countries')


#Language
class LanguagesListView(AlphabetOrderPaginationMixin, ListView):
    model = Language
    template_name = 'languages.html'
    context_object_name = 'languages'
    paginate_by = 10
    default_order_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['language_create_url'] = reverse('language_create')
        return context


class LanguageDetailView(AlphabetOrderPaginationRelatedMixin, DetailView):
    model = Language
    template_name = "language.html"
    context_object_name = "language"
    default_order_field = "title"  # řazení písní podle názvu

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # FK reverzní vztah: song_set
        songs_qs = self.object.songs
        page_obj = self.filter_order_paginate_queryset(songs_qs)

        context["songs"] = page_obj
        context["paginate_options"] = self.paginate_options
        context["alphabet"] = self.get_alphabet()
        return context


class LanguageCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'  # Reusable form template
    form_class = LanguageModelForm     # Use custom form with validation
    success_url = reverse_lazy('languages')  # Redirect after success

    # form_valid is not needed --> CreateView handles saving


class LanguageUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = LanguageModelForm
    model = Language
    success_url = reverse_lazy('languages')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class LanguageDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Language
    success_url = reverse_lazy('language')


# Genre Views
class GenresListView(AlphabetOrderPaginationMixin, ListView):
    model = Genre
    template_name = 'genres.html'
    context_object_name = 'genres'
    paginate_by = 10
    default_order_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_create_url'] = reverse('genre_create')
        return context


class GenreDetailView(AlphabetOrderPaginationRelatedMixin, DetailView):
    model = Genre
    template_name = "genre.html"
    context_object_name = "genre"
    default_order_field = "title"  # řadíme podle názvu písně

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        songs_qs = self.object.song_set.all()
        page_obj = self.filter_order_paginate_queryset(songs_qs)

        context["songs"] = page_obj
        context["paginate_options"] = self.paginate_options
        context["alphabet"] = self.get_alphabet()
        return context


class GenreCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form.html'  # Reusable form template
    form_class = GenreModelForm     # Use custom form with validation
    success_url = reverse_lazy('genres')  # Redirect after success
    # form_valid is not needed --> CreateView handles saving


class GenreUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = GenreModelForm
    model = Genre
    success_url = reverse_lazy('genres')

    def form_invalid(self, form):
        print('Form invalid')
        return super().form_invalid(form)


class GenreDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Genre
    success_url = reverse_lazy('genres')


def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    context = {'query': query}

    if query:
        songs = Song.objects.filter(title__icontains=query)[:5]
        albums = Album.objects.filter(title__icontains=query)[:3]
        contributors = Contributor.objects.filter(
            Q(stage_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:3]
    else:
        songs = albums = contributors = []

    context.update({'songs': songs, 'albums': albums, 'contributors': contributors})
    html = render_to_string("partials/search_dropdown.html", context)
    return HttpResponse(html)