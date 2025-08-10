import os
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
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

from collections import OrderedDict

from mixins import AlphabetOrderPaginationMixin, AlphabetOrderPaginationRelatedMixin, \
    SongPerformanceBaseMixin
from viewer.forms import (
    GenreModelForm, CountryModelForm, ContributorModelForm, MusicGroupModelForm, SongModelForm, AlbumModelForm,
    ContributorSongPerformanceForm, LanguageModelForm, MusicGroupPerformanceForm,
    SongPerformanceContributorForm, SongPerformanceMusicGroupForm, ContributorMusicGroupMembershipForm,
    MusicGroupMembershipForm
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
        # Get 6 random albums with a valid cover image
        return Album.objects.exclude(cover_image='').exclude(cover_image__isnull=True).order_by('?')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        albums = context['albums']
        for index, album in enumerate(albums):
            file_path = os.path.join(settings.MEDIA_ROOT, album.cover_image.name)
            if os.path.exists(file_path):
                # Use real cover image URL if file exists
                album.image_url = album.cover_image.url
            else:
                # Use placeholder image if cover image file missing
                placeholder_number = (index % 6) + 1  # 1 to 6
                album.image_url = f"{settings.STATIC_URL}images/placeholders/placeholder{placeholder_number}.jpg"
        return context


# Song Views
class SongsListView(AlphabetOrderPaginationMixin, ListView):
    model = Song
    template_name = 'songs.html'
    context_object_name = 'songs'
    default_paginate_by = 10
    default_order_field = 'title'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add model info for templates
        context["model_name"] = self.model._meta.model_name
        context["app_label"] = self.model._meta.app_label
        return context


class SongDetailView(DetailView):
    model = Song
    template_name = 'song.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song = self.object

        # Query contributor performances with related contributor and role
        contributor_performances = SongPerformance.objects.filter(
            song=song,
            contributor__isnull=False
        ).select_related('contributor', 'contributor_role')

        # Group performances by contributor role category
        performances_by_category = OrderedDict()
        for perf in contributor_performances:
            category = perf.contributor_role.category if perf.contributor_role else 'other'
            if category not in performances_by_category:
                performances_by_category[category] = []
            performances_by_category[category].append(perf)

        # Query music group performances with related group and role
        music_group_performances = SongPerformance.objects.filter(
            song=song,
            music_group__isnull=False
        ).select_related('music_group', 'music_group_role')

        # Store music group performances by role
        performances_by_role = OrderedDict()
        performances_by_role['music_groups'] = list(music_group_performances)

        context['performances_by_category'] = performances_by_category
        context['music_group_performances_by_role'] = performances_by_role

        return context


class SongCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = SongModelForm
    success_url = reverse_lazy('songs')
    permission_required = 'viewer.add_song'


class SongUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = SongModelForm
    model = Song
    success_url = reverse_lazy('songs')
    permission_required = 'viewer.change_song'

    def form_invalid(self, form):
        # Log form invalid case
        print('Form invalid')
        return super().form_invalid(form)


class SongDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Song
    success_url = reverse_lazy('songs')
    permission_required = 'viewer.delete_song'


# Song performance for Contributor
class SongPerformanceContributorCreateView(PermissionRequiredMixin, SongPerformanceBaseMixin, CreateView):
    form_class = SongPerformanceContributorForm
    permission_required = 'viewer.add_songperformance'


class SongPerformanceContributorUpdateView(PermissionRequiredMixin, UpdateView):
    model = SongPerformance
    form_class = SongPerformanceContributorForm
    template_name = "form.html"
    permission_required = 'viewer.change_songperformance'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass song to the form
        kwargs['song'] = self.object.song
        return kwargs

    def get_success_url(self):
        # Redirect to the song detail page after update
        return reverse('song', kwargs={'pk': self.object.song.pk})


class SongPerformanceContributorDeleteView(PermissionRequiredMixin, DeleteView):
    model = SongPerformance
    template_name = "confirm_delete.html"
    permission_required = 'viewer.delete_songperformance'

    def get_success_url(self):
        # Redirect to the song detail page after delete
        song = self.object.song
        return reverse('song', kwargs={'pk': song.pk})


# Song performance for music group
class SongPerformanceMusicGroupCreateView(PermissionRequiredMixin, SongPerformanceBaseMixin, CreateView):
    form_class = SongPerformanceMusicGroupForm
    permission_required = 'viewer.add_songperformance'


class SongPerformanceMusicGroupUpdateView(PermissionRequiredMixin, UpdateView):
    model = SongPerformance
    form_class = SongPerformanceMusicGroupForm
    template_name = "form.html"
    permission_required = 'viewer.change_songperformance'

    def get_success_url(self):
        # Redirect to the song detail page after update
        song = self.object.song
        return reverse('song', kwargs={'pk': song.pk})


class SongPerformanceMusicGroupDeleteView(PermissionRequiredMixin, DeleteView):
    model = SongPerformance
    template_name = "confirm_delete.html"
    permission_required = 'viewer.delete_songperformance'

    def get_success_url(self):
        # Redirect to the song detail page after delete
        song = self.object.song
        return reverse('song', kwargs={'pk': song.pk})


# Album Views
class AlbumsListView(ListView):
    model = Album
    template_name = 'albums.html'
    context_object_name = 'albums'
    paginate_by = 10

    def get_ordering(self):
        # Determine ordering direction for albums
        order = self.request.GET.get('order', 'asc')
        return 'title' if order == 'asc' else '-title'

    def get_paginate_by(self, queryset):
        # Get pagination count from GET or fallback
        try:
            return int(self.request.GET.get('paginate_by', self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by

    def get_queryset(self):
        queryset = super().get_queryset()
        letter = self.request.GET.get("letter")
        if letter:
            # Filter albums starting with selected letter
            queryset = queryset.filter(title__istartswith=letter)
        return queryset.order_by(self.get_ordering())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add pagination options and alphabet for templates
        context['paginate_options'] = [10, 20, 50, 100]
        context['alphabet'] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        context['model_name'] = 'album'  # Important for templates
        context['app_label'] = 'viewer'  # Adjust to your app name
        return context


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'album.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object

        # Get related album songs ordered by their order field
        album_songs = AlbumSong.objects.filter(album=album).select_related('song').order_by('order')

        genres = album.genres_list()
        languages = album.languages_list()
        contributors_by_category = album.contributors_by_category()
        groups_by_role = album.groups_by_role()

        genre_label = "Genre" if genres.count() == 1 else "Genres"
        language_label = "Language" if languages.count() == 1 else "Languages"

        context.update({
            'album_songs': album_songs,
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


class AlbumCreateView(PermissionRequiredMixin, CreateView):
    model = Album
    form_class = AlbumModelForm
    template_name = 'form.html'
    success_url = reverse_lazy('albums')
    permission_required = 'viewer.add_album'

    def form_valid(self, form):
        # Save album and handle cover image upload
        self.object = form.save(commit=False)

        if self.request.FILES.get('cover_image'):
            self.object.cover_image = self.request.FILES['cover_image']

        self.object.save()
        form.save_m2m()  # Save many-to-many relations

        songs = form.cleaned_data.get('songs', [])
        if not songs:
            form.add_error('songs', 'At least one song must be selected.')
            return self.form_invalid(form)

        # Remove existing album-song links before recreating
        AlbumSong.objects.filter(album=self.object).delete()

        # Create AlbumSong relations with ordering
        for index, song in enumerate(songs, start=1):
            AlbumSong.objects.create(
                album=self.object,
                song=song,
                order=index
            )

        return redirect(self.get_success_url())


class AlbumUpdateView(PermissionRequiredMixin, UpdateView):
    model = Album
    form_class = AlbumModelForm
    template_name = 'form.html'
    success_url = reverse_lazy('albums')
    permission_required = 'viewer.change_album'

    def form_valid(self, form):
        # Update album and handle cover image upload
        self.object = form.save(commit=False)

        if self.request.FILES.get('cover_image'):
            self.object.cover_image = self.request.FILES['cover_image']

        self.object.save()
        form.save_m2m()

        songs = form.cleaned_data.get('songs', [])
        if not songs:
            form.add_error('songs', 'At least one song must be selected.')
            return self.form_invalid(form)

        # Remove existing album-song links before recreating
        AlbumSong.objects.filter(album=self.object).delete()

        # Create AlbumSong relations with ordering
        for index, song in enumerate(songs, start=1):
            AlbumSong.objects.create(
                album=self.object,
                song=song,
                order=index
            )

        return redirect(self.get_success_url())


class AlbumDeleteView(PermissionRequiredMixin, DeleteView):
    model = Album
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('albums')
    permission_required = 'viewer.delete_album'


class AlbumSongOrderUpdateView(PermissionRequiredMixin, View):
    permission_required = 'viewer.change_albumsong'

    @method_decorator(require_POST)
    def post(self, request, album_pk):
        album = get_object_or_404(Album, pk=album_pk)
        album_songs = list(AlbumSong.objects.filter(album=album))
        max_order = len(album_songs)

        new_orders = {}
        errors = []

        # Validate new order values from POST data
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

        # Save new orders atomically
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
    paginate_per_column = 5  # Default items per column

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        letter = self.request.GET.get('letter')

        # Try to get items per column from GET parameter
        try:
            self.paginate_per_column = int(self.request.GET.get('paginate_per_column', self.paginate_per_column))
        except (ValueError, TypeError):
            pass  # Use default if invalid

        def get_paginated_contributors(category, page_param):
            # Query contributors by category with prefetching roles
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

            # Add role_names attribute listing roles as a string
            for contributor in page_obj.object_list:
                roles = contributor.song_performances.values_list('contributor_role__name', flat=True).distinct()
                contributor.role_names = ', '.join(sorted(set(roles))) if roles else '—'

            return page_obj, paginator

        # Get paginated contributors for all categories
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

        # Fetch song performances with related song and contributor_role
        song_performances = SongPerformance.objects.filter(contributor=contributor).select_related('song',
                                                                                                   'contributor_role')

        # Group performances by contributor role category
        songs_by_category = {}
        for perf in song_performances:
            category = perf.contributor_role.category if perf.contributor_role else 'other'
            songs_by_category.setdefault(category, []).append(perf)

        # Fetch other related data
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


class ContributorCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = ContributorModelForm
    success_url = reverse_lazy('contributors')
    permission_required = 'viewer.add_contributor'


class ContributorUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = ContributorModelForm
    model = Contributor
    success_url = reverse_lazy('contributors')
    permission_required = 'viewer.change_contributor'

    def form_invalid(self, form):
        # Log form invalid case
        print('Form invalid')
        return super().form_invalid(form)


class ContributorDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Contributor
    success_url = reverse_lazy('contributors')
    permission_required = 'viewer.delete_contributor'



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
        # Add annotation counting unique contributors linked by SongPerformance
        qs = qs.annotate(contributors_count=Count('songperformance__contributor', distinct=True))
        return qs


class ContributorRoleDetailView(AlphabetOrderPaginationRelatedMixin, DetailView):
    model = ContributorRole
    template_name = 'contributor-role.html'
    context_object_name = 'contributor_role'
    default_order_field = 'last_name'  # order contributors by last name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get contributors who have this role in any SongPerformance
        contributors_qs = Contributor.objects.filter(
            song_performances__contributor_role=self.object
        ).distinct()

        # Use mixin for pagination, ordering, and alphabet filtering
        page_obj = self.filter_order_paginate_queryset(contributors_qs)

        context['page_obj'] = page_obj
        context['paginate_options'] = self.paginate_options
        context['alphabet'] = self.get_alphabet()

        return context


class ContributorRoleCreateView(PermissionRequiredMixin, CreateView):
    model = ContributorRole
    fields = ['name', 'category']
    success_url = reverse_lazy('contributor_roles')
    template_name = 'form.html'
    permission_required = 'viewer.add_contributorrole'


class ContributorRoleUpdateView(PermissionRequiredMixin, UpdateView):
    model = ContributorRole
    fields = ['name', 'category']
    success_url = reverse_lazy('roles')
    template_name = 'form.html'
    permission_required = 'viewer.change_contributorrole'


class ContributorRoleDeleteView(PermissionRequiredMixin, DeleteView):
    model = ContributorRole
    success_url = reverse_lazy('roles')
    template_name = 'confirm_delete.html'
    permission_required = 'viewer.delete_contributorrole'


# Contributor song performance
class ContributorSongPerformanceCreateView(PermissionRequiredMixin, CreateView):
    model = SongPerformance
    form_class = ContributorSongPerformanceForm
    template_name = 'form.html'
    permission_required = 'viewer.add_songperformance'

    def get_initial(self):
        # Pre-fill contributor in form initial data
        initial = super().get_initial()
        initial['contributor'] = self.kwargs['contributor_pk']
        return initial

    def get_success_url(self):
        # Redirect to contributor detail after success
        return reverse('contributor', kwargs={'pk': self.kwargs['contributor_pk']})

    def form_valid(self, form):
        # Force contributor from URL to avoid tampering
        contributor_pk = self.kwargs['contributor_pk']
        contributor = Contributor.objects.get(pk=contributor_pk)
        form.instance.contributor = contributor
        return super().form_valid(form)


class ContributorSongPerformanceUpdateView(PermissionRequiredMixin, UpdateView):
    model = SongPerformance
    form_class = ContributorSongPerformanceForm
    template_name = 'form.html'
    success_url = reverse_lazy('contributors')
    permission_required = 'viewer.change_songperformance'


class ContributorSongPerformanceDeleteView(PermissionRequiredMixin, DeleteView):
    model = SongPerformance
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('contributors')
    permission_required = 'viewer.delete_songperformance'


# Contributor music group
class ContributorMusicGroupMembershipCreateView(PermissionRequiredMixin, CreateView):
    model = MusicGroupMembership
    form_class = ContributorMusicGroupMembershipForm
    template_name = 'form.html'
    permission_required = 'viewer.add_musicgroupmembership'

    def get_success_url(self):
        # Redirect to contributor detail after success
        return reverse_lazy('contributor', kwargs={'pk': self.object.member.pk})

    def form_valid(self, form):
        # Force member to contributor from URL
        contributor_pk = self.kwargs['contributor_pk']
        contributor = Contributor.objects.get(pk=contributor_pk)
        form.instance.member = contributor
        return super().form_valid(form)


class ContributorMusicGroupMembershipUpdateView(PermissionRequiredMixin, UpdateView):
    model = MusicGroupMembership
    form_class = ContributorMusicGroupMembershipForm
    template_name = 'form.html'
    permission_required = 'viewer.change_musicgroupmembership'

    def get_success_url(self):
        # Redirect to contributor detail after update
        return reverse_lazy('contributor', kwargs={'pk': self.object.member.pk})


class ContributorMusicGroupMembershipDeleteView(PermissionRequiredMixin, DeleteView):
    model = MusicGroupMembership
    template_name = 'confirm_delete.html'
    permission_required = 'viewer.delete_musicgroupmembership'

    def get_success_url(self):
        # Redirect to contributor detail after delete
        return reverse_lazy('contributor', kwargs={'pk': self.object.member.pk})


# Music groups
class MusicGroupsListView(ListView):
    model = MusicGroup
    template_name = 'music-groups.html'
    context_object_name = 'music_groups'
    paginate_by = 10

    def get_ordering(self):
        # Determine ordering direction for music groups by name
        order = self.request.GET.get('order', 'asc')
        return 'name' if order == 'asc' else '-name'

    def get_paginate_by(self, queryset):
        # Get pagination size from GET parameter or fallback
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
        # Provide pagination options and alphabet for UI
        context['paginate_options'] = [10, 20, 50, 100]
        context['alphabet'] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return context


class MusicGroupDetailView(DetailView):
    template_name = 'music-group.html'
    model = MusicGroup
    context_object_name = 'music_group'


class MusicGroupCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = MusicGroupModelForm
    success_url = reverse_lazy('music_groups')
    permission_required = 'viewer.add_musicgroup'


class MusicGroupUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = MusicGroupModelForm
    model = MusicGroup
    success_url = reverse_lazy('music_groups')
    permission_required = 'viewer.change_musicgroup'

    def form_invalid(self, form):
        # Log form invalid event
        print('Form invalid')
        return super().form_invalid(form)


class MusicGroupDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = MusicGroup
    success_url = reverse_lazy('music_groups')
    permission_required = 'viewer.delete_musicgroup'


# Music group membership
class MusicGroupMembershipCreateView(PermissionRequiredMixin, CreateView):
    model = MusicGroupMembership
    form_class = MusicGroupMembershipForm
    permission_required = 'viewer.add_musicgroupmembership'
    template_name = 'form.html'

    def get_initial(self):
        # Pre-fill music group if given in GET parameters
        initial = super().get_initial()
        music_group_id = self.request.GET.get('music_group')
        if music_group_id:
            initial['music_group'] = music_group_id
        return initial

    def get_success_url(self):
        # Redirect to music group detail after creation
        return reverse_lazy('music_group', kwargs={'pk': self.object.music_group.pk})


class MusicGroupMembershipUpdateView(PermissionRequiredMixin, UpdateView):
    model = MusicGroupMembership
    form_class = MusicGroupMembershipForm
    permission_required = 'viewer.change_musicgroupmembership'
    template_name = 'form.html'

    def get_success_url(self):
        # Redirect to music group detail after update
        return reverse_lazy('music_group', kwargs={'pk': self.object.music_group.pk})


class MusicGroupMembershipDeleteView(PermissionRequiredMixin, DeleteView):
    model = MusicGroupMembership
    permission_required = 'viewer.delete_musicgroupmembership'
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        # Redirect to music group detail after delete
        return reverse_lazy('music_group', kwargs={'pk': self.object.music_group.pk})


# Music group roles
class MusicGroupRolesListView(AlphabetOrderPaginationMixin, ListView):
    model = MusicGroupRole
    template_name = 'music-group-roles.html'
    context_object_name = 'page_obj'
    default_order_field = 'name'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        # Annotate with count of unique music groups linked by songperformances
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
        # Collect unique music groups linked to performances
        music_groups = {p.music_group for p in performances if p.music_group is not None}
        context['music_groups'] = sorted(music_groups, key=lambda g: g.name)
        return context


class MusicGroupRoleCreateView(PermissionRequiredMixin, CreateView):
    model = MusicGroupRole
    fields = ['name']
    success_url = reverse_lazy('music_group_roles')
    template_name = 'form.html'
    permission_required = 'viewer.add_musicgrouprole'


class MusicGroupRoleUpdateView(PermissionRequiredMixin, UpdateView):
    model = MusicGroupRole
    fields = ['name']
    success_url = reverse_lazy('music_group_roles')
    template_name = 'form.html'
    permission_required = 'viewer.change_musicgrouprole'


class MusicGroupRoleDeleteView(PermissionRequiredMixin, DeleteView):
    model = MusicGroupRole
    success_url = reverse_lazy('music_group_roles')
    template_name = 'confirm_delete.html'
    permission_required = 'viewer.delete_musicgrouprole'


# Country Views
class CountriesListView(AlphabetOrderPaginationMixin, ListView):
    model = Country
    template_name = 'countries.html'
    context_object_name = 'countries'
    default_order_field = 'name'  # adjust to your Country model field
    default_paginate_by = 10


class CountryDetailView(DetailView):
    template_name = 'country.html'
    model = Country
    context_object_name = 'country'


class CountryCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'form.html'
    form_class = CountryModelForm
    success_url = reverse_lazy('countries')
    permission_required = 'viewer.add_country'


class CountryUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = CountryModelForm
    model = Country
    success_url = reverse_lazy('countries')
    permission_required = 'viewer.change_country'

    def form_invalid(self, form):
        # Log form invalid event
        print('Form invalid')
        return super().form_invalid(form)


class CountryDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Country
    success_url = reverse_lazy('countries')
    permission_required = 'viewer.delete_country'


# Language
class LanguagesListView(AlphabetOrderPaginationMixin, ListView):
    model = Language
    template_name = 'languages.html'
    context_object_name = 'languages'
    paginate_by = 10
    default_order_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add create URL for languages in context
        context['language_create_url'] = reverse('language_create')
        return context


class LanguageDetailView(AlphabetOrderPaginationRelatedMixin, DetailView):
    model = Language
    template_name = "language.html"
    context_object_name = "language"
    default_order_field = "title"  # order songs by title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use reverse FK: song_set for related songs
        songs_qs = self.object.songs
        page_obj = self.filter_order_paginate_queryset(songs_qs)

        context["songs"] = page_obj
        context["paginate_options"] = self.paginate_options
        context["alphabet"] = self.get_alphabet()
        return context


class LanguageCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'form.html'  # reusable form template
    form_class = LanguageModelForm  # custom form with validation
    success_url = reverse_lazy('languages')  # redirect after success
    permission_required = 'viewer.add_language'

    # form_valid is handled by CreateView


class LanguageUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = LanguageModelForm
    model = Language
    success_url = reverse_lazy('languages')
    permission_required = 'viewer.change_language'

    def form_invalid(self, form):
        # Log form invalid event
        print('Form invalid')
        return super().form_invalid(form)


class LanguageDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Language
    success_url = reverse_lazy('language')
    permission_required = 'viewer.delete_language'


# Genre Views
class GenresListView(AlphabetOrderPaginationMixin, ListView):
    model = Genre
    template_name = 'genres.html'
    context_object_name = 'genres'
    paginate_by = 10
    default_order_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add create URL for genres in context
        context['genre_create_url'] = reverse('genre_create')
        return context


class GenreDetailView(AlphabetOrderPaginationRelatedMixin, DetailView):
    model = Genre
    template_name = "genre.html"
    context_object_name = "genre"
    default_order_field = "title"  # order songs by title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        songs_qs = self.object.song_set.all()
        page_obj = self.filter_order_paginate_queryset(songs_qs)

        context["songs"] = page_obj
        context["paginate_options"] = self.paginate_options
        context["alphabet"] = self.get_alphabet()
        return context


class GenreCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'form.html'  # reusable form template
    form_class = GenreModelForm  # custom form with validation
    success_url = reverse_lazy('genres')  # redirect after success
    permission_required = 'viewer.add_genre'
    # form_valid is handled by CreateView


class GenreUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'form.html'
    form_class = GenreModelForm
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'viewer.change_genre'

    def form_invalid(self, form):
        # Log form invalid event
        print('Form invalid')
        return super().form_invalid(form)


class GenreDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'confirm_delete.html'
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'viewer.delete_genre'


# SEARCH Views
def search_view(request):
    query = request.GET.get('q', '').strip()
    songs = []
    external_songs = []

    if query:
        # Local search results for songs
        songs = Song.objects.filter(title__icontains=query)

        # External MusicBrainz results, always shown
        url = "https://musicbrainz.org/ws/2/recording"
        params = {
            "query": query,
            "fmt": "json",
            "limit": 10
        }
        headers = {
            "User-Agent": "MusicLibrary/1.0 ( your-email@example.com )"
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                for rec in data.get("recordings", []):
                    external_songs.append({
                        "title": rec.get("title"),
                        "artist": rec["artist-credit"][0]["name"] if rec.get("artist-credit") else "Unknown"
                    })
        except requests.RequestException:
            # Ignore external API errors silently
            pass

    context = {
        'query': query,
        'songs': songs,
        'external_songs': external_songs
    }
    return render(request, 'search_results.html', context)


def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    context = {'query': query}

    if query:
        # Limit local search suggestions for songs, albums, and contributors
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
    html = render_to_string("search_dropdown.html", context)
    return HttpResponse(html)

