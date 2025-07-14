from django.contrib import admin

from viewer.models import Genre, Country, Artist, Group

admin.site.register(Genre)
admin.site.register(Country)
admin.site.register(Artist)
admin.site.register(Group)
