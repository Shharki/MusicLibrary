from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse

from viewer.models import SongPerformance, Song


class AlphabetOrderPaginationMixin:
    """Mixin for pagination and filtering queryset by alphabet and ordering by specified field."""

    default_order_field = "title"  # default field used for ordering
    paginate_options = [10, 20, 50, 100]  # options for items per page
    default_paginate_by = 10  # default items per page

    def get_ordering(self):
        # Determine ordering direction from GET parameter 'order' (asc/desc)
        order = self.request.GET.get("order", "asc")
        return self.default_order_field if order == "asc" else f"-{self.default_order_field}"

    def get_paginate_by(self, queryset):
        # Get items per page from GET parameter or fallback to default
        try:
            return int(self.request.GET.get("paginate_by", self.default_paginate_by))
        except (TypeError, ValueError):
            return self.default_paginate_by

    def get_queryset(self):
        # Apply filtering by first letter and ordering to base queryset
        queryset = super().get_queryset()
        letter = self.request.GET.get("letter")
        if letter:
            # Filter items starting with the given letter (case-insensitive)
            queryset = queryset.filter(**{f"{self.default_order_field}__istartswith": letter})
        ordering = self.get_ordering()
        return queryset.order_by(ordering)

    def get_context_data(self, **kwargs):
        # Add pagination options and alphabet list to context for templates
        context = super().get_context_data(**kwargs)
        context["paginate_options"] = self.paginate_options
        context["alphabet"] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return context


class AlphabetOrderPaginationRelatedMixin:
    """Similar mixin but for filtering, ordering and paginating a passed queryset, returning a paginated page object."""

    default_order_field = "title"
    paginate_options = [10, 20, 50, 100]
    default_paginate_by = 10

    def get_letter(self):
        # Get filtering letter from GET parameter
        return self.request.GET.get("letter")

    def get_ordering(self):
        # Get ordering direction from GET parameter
        order = self.request.GET.get("order", "asc")
        return self.default_order_field if order == "asc" else f"-{self.default_order_field}"

    def get_paginate_by(self):
        # Get items per page or fallback to default
        try:
            return int(self.request.GET.get("paginate_by", self.default_paginate_by))
        except (TypeError, ValueError):
            return self.default_paginate_by

    def filter_order_paginate_queryset(self, queryset):
        # Filter queryset by letter, order it, paginate and return page object
        letter = self.get_letter()
        if letter:
            queryset = queryset.filter(**{f"{self.default_order_field}__istartswith": letter})

        ordering = self.get_ordering()
        queryset = queryset.order_by(ordering)

        paginate_by = self.get_paginate_by()
        paginator = Paginator(queryset, paginate_by)

        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return page_obj

    def get_alphabet(self):
        # Return alphabet list for templates
        return list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class ContributorsByCategoryMixin:
    """Mixin to categorize contributors of a song by their role category, returning dict of categories with contributor performances."""

    performance_related_fields = ("contributor", "contributor_role")

    def get_contributors_by_category(self, song):
        # Fetch all performances for the song with related contributor and role
        performances = song.performances.select_related(*self.performance_related_fields)

        contributors_by_category = {}

        # Group performances by contributor role category name
        for performance in performances:
            category = performance.contributor_role.name
            if category not in contributors_by_category:
                contributors_by_category[category] = []

            contributors_by_category[category].append(
                (
                    performance,
                    performance.contributor,
                    [performance.contributor_role],
                )
            )
        return contributors_by_category

    def get_context_data(self, **kwargs):
        # Add categorized contributors dict to context for template rendering
        context = super().get_context_data(**kwargs)
        context["contributors_by_category"] = self.get_contributors_by_category(self.get_object())
        return context


class SongPerformanceBaseMixin:
    """Base mixin for SongPerformance forms that pre-fills the song from GET or instance and sets success URL."""

    model = SongPerformance
    template_name = "form.html"

    def get_song(self):
        # Try to get song from GET parameter 'song', fallback to instance song for updates
        song_pk = self.request.GET.get('song')
        if song_pk:
            return get_object_or_404(Song, pk=song_pk)
        if hasattr(self, 'object') and self.object:
            return self.object.song
        return None

    def get_initial(self):
        # Pre-fill form initial data with song if available
        initial = super().get_initial()
        song = self.get_song()
        if song:
            initial['song'] = song
        return initial

    def form_valid(self, form):
        # Assign song to form instance before saving
        song = self.get_song()
        if song:
            form.instance.song = song
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to song detail page after successful save if song known
        song = self.get_song()
        if song:
            return reverse('song', kwargs={'pk': song.pk})
        return super().get_success_url()
