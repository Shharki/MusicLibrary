from django.contrib import admin

from viewer.models import (
    Genre, Country, Language, Contributor, MusicGroup, ContributorPreviousName, ContributorRole, \
    MusicGroupMembership, Song, SongPerformance, Album, MusicGroupRole, AlbumSong
)

admin.site.register(Genre)
admin.site.register(Country)
admin.site.register(Language)
admin.site.register(Contributor)
admin.site.register(MusicGroup)
admin.site.register(ContributorPreviousName)
admin.site.register(ContributorRole)
admin.site.register(MusicGroupMembership)
admin.site.register(MusicGroupRole)
admin.site.register(Song)
admin.site.register(SongPerformance)
admin.site.register(Album)
admin.site.register(AlbumSong)
