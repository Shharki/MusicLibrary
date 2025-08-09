from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse

from viewer.models import SongPerformance, Song


class AlphabetOrderPaginationMixin:
    default_order_field = "title"
    paginate_options = [10, 20, 50, 100]
    default_paginate_by = 10

    def get_ordering(self):
        order = self.request.GET.get("order", "asc")
        return self.default_order_field if order == "asc" else f"-{self.default_order_field}"

    def get_paginate_by(self, queryset):
        try:
            return int(self.request.GET.get("paginate_by", self.default_paginate_by))
        except (TypeError, ValueError):
            return self.default_paginate_by

    def get_queryset(self):
        queryset = super().get_queryset()
        order = self.request.GET.get("order", "asc")
        letter = self.request.GET.get("letter")

        if letter:
            queryset = queryset.filter(**{f"{self.default_order_field}__istartswith": letter})

        ordering = self.get_ordering()
        return queryset.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paginate_options"] = self.paginate_options
        context["alphabet"] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return context


class AlphabetOrderPaginationRelatedMixin:
    default_order_field = "title"
    paginate_options = [10, 20, 50, 100]
    default_paginate_by = 10

    def get_letter(self):
        return self.request.GET.get("letter")

    def get_ordering(self):
        order = self.request.GET.get("order", "asc")
        return self.default_order_field if order == "asc" else f"-{self.default_order_field}"

    def get_paginate_by(self):
        try:
            return int(self.request.GET.get("paginate_by", self.default_paginate_by))
        except (TypeError, ValueError):
            return self.default_paginate_by

    def filter_order_paginate_queryset(self, queryset):
        letter = self.request.GET.get("letter")
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
        return list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class ContributorsByCategoryMixin:
    """
    Přidá do contextu 'contributors_by_category', seskupené podle role (category)
    ve formátu:
    {
        "Zpěv": [
            (performance, contributor, [role1, role2]),
            ...
        ],
        ...
    }
    """
    performance_related_fields = ("contributor", "contributor_role")

    def get_contributors_by_category(self, song):
        performances = song.performances.select_related(*self.performance_related_fields)

        contributors_by_category = {}

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
        context = super().get_context_data(**kwargs)
        context["contributors_by_category"] = self.get_contributors_by_category(self.get_object())
        return context


class SongPerformanceBaseMixin:
    model = SongPerformance
    template_name = "form.html"

    def get_song(self):
        # Nejprve z GET parametru, pokud není, z instance (pro update)
        song_pk = self.request.GET.get('song')
        if song_pk:
            return get_object_or_404(Song, pk=song_pk)
        # Pokud je instance (např. update), vrať song z ní
        if hasattr(self, 'object') and self.object:
            return self.object.song
        return None

    def get_initial(self):
        initial = super().get_initial()
        song = self.get_song()
        if song:
            initial['song'] = song
        return initial

    def form_valid(self, form):
        song = self.get_song()
        if song:
            form.instance.song = song
        return super().form_valid(form)

    def get_success_url(self):
        song = self.get_song()
        if song:
            return reverse('song', kwargs={'pk': song.pk})
        return super().get_success_url()
