from django.db.models import Model, CharField, DateField, ForeignKey, TextField, DateTimeField, SET_NULL, \
    ManyToManyField, CASCADE, PositiveIntegerField, ImageField


class Genre(Model):
    name = CharField(max_length=64, null=False, blank=False, unique=True)

    class Meta:
        ordering = ['name']

    def __repr__(self):
        return f"Genre(name={self.name})"

    def __str__(self):
        return self.name


class Country(Model):
    name = CharField(max_length=64, null=False, blank=False, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'

    def __repr__(self):
        return f"Country(name={self.name})"

    def __str__(self):
        return self.name


class Language(Model):
    name = CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Language(name={self.name})"


class Contributor(Model):
    first_name = CharField(max_length=64, null=False, blank=False)
    middle_name = CharField(max_length=64, null=True, blank=True)
    last_name = CharField(max_length=64, null=False, blank=False)
    stage_name = CharField(max_length=64, null=True, blank=True)
    date_of_birth = DateField(null=True, blank=True, unique=True)
    date_of_death = DateField(null=True, blank=True, unique=True)
    country = ForeignKey(Country, null=True, blank=True, on_delete=SET_NULL, related_name='contributors')
    bio = TextField(null=True, blank=True)


    class Meta:
        ordering = ['last_name', 'first_name']

    def __repr__(self):
        return f"Contributor({self.__str__()})"

    def __str__(self):
        return self.stage_name or f"{self.first_name} {self.last_name}"


class ContributorPreviousName(Model):
    contributor = ForeignKey(Contributor, on_delete=CASCADE, related_name="previous_names")
    first_name = CharField(max_length=64)
    middle_name = CharField(max_length=64, null=True, blank=True)
    last_name = CharField(max_length=64)

    class Meta:
        ordering = ['last_name', 'first_name']
        db_table = 'viewer_contributor_previous_name'

    def __str__(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}"

    def __repr__(self):
        return f"ContributorPreviousName({self.__str__()})"


class ContributorRole(Model):
    name = CharField(max_length=64, unique=True)

    class Meta:
        ordering = ['name']
        db_table = 'viewer_contributor_role'

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"ContributorRole(name={self.name})"


class MusicGroupRole(Model):
    name = CharField(max_length=64, unique=True)

    class Meta:
        ordering = ['name']
        db_table = 'viewer_music_group_role'

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"MusicGroupRole(name={self.name})"


class MusicGroup(Model):
    name = CharField(max_length=64, null=False, blank=False, unique=True)
    bio = TextField(null=True, blank=True)
    founded = DateField(null=True, blank=True)
    disbanded = DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        db_table = 'viewer_music_group'

    def __repr__(self):
        return f"MusicGroup(name={self.name})"

    def __str__(self):
        return self.name


class MusicGroupMembership(Model):
    contributor = ForeignKey(Contributor, on_delete=CASCADE, related_name="memberships")
    music_group = ForeignKey(MusicGroup, on_delete=CASCADE, related_name="members")
    contributor_role = ManyToManyField(ContributorRole, blank=True)
    from_date = DateField(null=True, blank=True)
    to_date = DateField(null=True, blank=True)

    class Meta:
        ordering = ['contributor', 'music_group']
        db_table = 'viewer_music_group_membership'

    def __str__(self):
        return f"{self.contributor} in {self.music_group}"

    def __repr__(self):
        return f"MusicGroupMembership({self.__str__()})"


class Song(Model):
    title = CharField(max_length=128)
    genres = ManyToManyField(Genre, blank=True)
    duration = PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)
    released_year = PositiveIntegerField(null=True, blank=True)
    summary = TextField(null=True, blank=True)
    lyrics = TextField(null=True, blank=True)
    language = ForeignKey(Language, on_delete=SET_NULL, null=True, blank=True, related_name="songs")

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Song(title={self.title})"


class SongPerformance(Model):
    song = ForeignKey(Song, on_delete=CASCADE, related_name="performances")
    contributor = ForeignKey(Contributor, on_delete=CASCADE, null=True, blank=True, related_name="song_performances")
    contributor_role = ForeignKey(ContributorRole, on_delete=SET_NULL, null=True, blank=True)
    music_group = ForeignKey(MusicGroup, on_delete=CASCADE, null=True, blank=True, related_name="song_performances")
    music_group_role = ForeignKey(MusicGroupRole, on_delete=SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['song']
        db_table = 'viewer_song_performance'

    def __str__(self):
        return f"Performance of {self.song}"

    def __repr__(self):
        return f"SongPerformance(song={self.song})"


class Album(Model):
    title = CharField(max_length=128)
    songs = ManyToManyField(Song, blank=True, related_name="albums")
    released_year = PositiveIntegerField(null=True, blank=True)
    summary = TextField(null=True, blank=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Album"
        verbose_name_plural = "Albums"

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Album(title={self.title})"