from django.contrib import admin

from viewer.models import Genre, Country, Language, Artist, Group

admin.site.register(Genre)
admin.site.register(Country)
admin.site.register(Language)
admin.site.register(Artist)
admin.site.register(Group)
