from django.contrib import admin

from viewer.models import (
    Genre, Country, Language, Contributor, MusicGroup, ContributorPreviousName, ContributorRole, \
    MusicGroupMembership, Song, SongPerformance, Album
)

admin.site.register(Genre)
admin.site.register(Country)
admin.site.register(Language)
admin.site.register(Contributor)
admin.site.register(MusicGroup)
admin.site.register(ContributorPreviousName)
admin.site.register(MusicGroupMembership)
admin.site.register(Song)
admin.site.register(SongPerformance)
admin.site.register(Album)
