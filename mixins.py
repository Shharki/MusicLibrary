from django.core.paginator import Paginator


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



