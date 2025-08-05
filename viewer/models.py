from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, DateField, ForeignKey, TextField, SET_NULL, \
    ManyToManyField, CASCADE, PositiveIntegerField, CheckConstraint, Q, Sum, ImageField

from viewer.utils import format_seconds


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
    date_of_birth = DateField(null=True, blank=True)
    date_of_death = DateField(null=True, blank=True)
    country = ForeignKey(Country, null=True, blank=True, on_delete=SET_NULL, related_name='contributors')
    bio = TextField(null=True, blank=True)

    class Meta:
        ordering = ['stage_name', 'last_name', 'first_name']

    def display_more(self):
        name = self.stage_name or f"{self.first_name} {self.middle_name + ' ' if self.middle_name else ''}{self.last_name}"
        years = []

        if self.date_of_birth:
            years.append(str(self.date_of_birth.year))
        else:
            years.append("")  # Because of the hyphenation

        if self.date_of_death:
            years.append(str(self.date_of_death.year))

        if any(years):
            name += f" ({'–'.join(years).strip('–')})"

        return name

    def __str__(self):
        return self.stage_name or f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"Contributor({self.__str__()})"

    def songs_grouped_by_category(self):
        """
        Vrátí dict: kategorie => [(song, role)]
        """
        performances = self.song_performances.select_related('song', 'contributor_role')
        result = {}

        for perf in performances:
            if perf.contributor_role and perf.song:
                category = perf.contributor_role.category
                role = perf.contributor_role.name
                song = perf.song

                if category not in result:
                    result[category] = []
                result[category].append((song, role))

        return result


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
    CATEGORY_CHOICES = [
        ('writer', 'Writer'),
        ('performer', 'Performer'),
        ('producer', 'Producer'),
        ('publisher', 'Publisher'),
        ('other', 'Other'),
    ]

    name = CharField(max_length=64, unique=True)
    category = CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

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
    country = ForeignKey(Country, null=True, blank=True, on_delete=SET_NULL, related_name='music_groups')

    class Meta:
        ordering = ['name']
        db_table = 'viewer_music_group'

    # Not used anywhere atm
    '''@property
    def all_members(self):
        return Contributor.objects.filter(
            memberships__music_group=self
        ).distinct().order_by('stage_name', 'last_name', 'first_name')'''

    def all_members_with_roles(self):
        return self.members.select_related('member').prefetch_related('member_role')

    @property
    def all_albums(self):
        return self.albums.order_by('released', 'title')

    def __repr__(self):
        return f"MusicGroup(name={self.name})"

    def __str__(self):
        return self.name


class MusicGroupMembership(Model):
    member = ForeignKey(Contributor, on_delete=CASCADE, related_name="memberships")
    music_group = ForeignKey(MusicGroup, on_delete=CASCADE, related_name="members")
    member_role = ManyToManyField(ContributorRole, blank=True)
    from_date = DateField(null=True, blank=True)
    to_date = DateField(null=True, blank=True)

    class Meta:
        ordering = ['music_group', 'member__last_name', 'member__first_name', 'member__stage_name']
        db_table = 'viewer_music_group_membership'

    def display_roles(self):
        return ', '.join(role.name for role in self.member_role.all())

    @property
    def active_period(self):
        if self.from_date and self.to_date:
            return f"[{self.from_date}–{self.to_date}]"
        elif self.from_date:
            return f"[{self.from_date}–]"
        elif self.to_date:
            return f"[–{self.to_date}]"
        return ""

    def __str__(self):
        return f"{self.member} in {self.music_group}"

    def __repr__(self):
        return f"MusicGroupMembership({self.__str__()})"


class Song(Model):
    title = CharField(max_length=128)
    artist = ManyToManyField(Contributor, blank=True, related_name="songs")
    music_group = ManyToManyField(MusicGroup, blank=True, related_name="songs")
    genre = ManyToManyField(Genre, blank=True)
    duration = PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)
    released = DateField(null=True, blank=True)
    summary = TextField(null=True, blank=True)
    lyrics = TextField(null=True, blank=True)
    language = ForeignKey(Language, on_delete=SET_NULL, null=True, blank=True, related_name="songs")

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Song(title={self.title})"

    def contributors_by_category(self):
        """
        Vrací dict: kategorie => list of (contributor, [role1, role2, ...])
        """
        performances = self.performances.select_related('contributor', 'contributor_role')
        contributors = {}

        for perf in performances:
            if perf.contributor and perf.contributor_role:
                category = perf.contributor_role.category
                role_name = perf.contributor_role.name
                contributor = perf.contributor

                if category not in contributors:
                    contributors[category] = []

                # Zkusíme najít, jestli už je contributor v seznamu
                for i, (existing_contributor, roles) in enumerate(contributors[category]):
                    if existing_contributor == contributor:
                        if role_name not in roles:
                            roles.append(role_name)
                        break
                else:
                    # Pokud tam ještě není, přidáme ho
                    contributors[category].append((contributor, [role_name]))

        return contributors

    def groups_by_role(self):
        """
        Vrátí dict: role => list of music groups bez duplicit
        """
        performances = self.performances.select_related('music_group', 'music_group_role')
        groups = {}

        seen = set()
        for perf in performances:
            if perf.music_group and perf.music_group_role:
                role = perf.music_group_role.name
                if role not in groups:
                    groups[role] = []
                if perf.music_group.id not in seen:
                    groups[role].append(perf.music_group)
                    seen.add(perf.music_group.id)

        return groups

    def first_album(self):
        return self.albums.first()

    def artists(self):
        return self.artist.all()

    def music_groups(self):
        return self.music_group.all()

    @property
    def format_seconds(self):
        if self.duration is None:
            return None
        mins, secs = divmod(self.duration, 60)
        return f"{mins}:{secs:02}"


class SongPerformance(Model):
    song = ForeignKey(Song, on_delete=CASCADE, related_name="performances")
    contributor = ForeignKey(Contributor, on_delete=CASCADE, null=True, blank=True, related_name="song_performances")
    contributor_role = ForeignKey(ContributorRole, on_delete=SET_NULL, null=True, blank=True)
    music_group = ForeignKey(MusicGroup, on_delete=CASCADE, null=True, blank=True, related_name="song_performances")
    music_group_role = ForeignKey(MusicGroupRole, on_delete=SET_NULL, null=True, blank=True)

    def clean(self):
        super().clean()

        if self.contributor and self.music_group:
            raise ValidationError("Only one of contributor or music group can be set.")
        if not self.contributor and not self.music_group:
            raise ValidationError("Either contributor or music group must be set.")

        if self.contributor and not self.contributor_role:
            raise ValidationError("If a contributor is set, contributor role must also be set.")
        if self.music_group and not self.music_group_role:
            raise ValidationError("If a music group is set, music group role must also be set.")

    class Meta:
        ordering = ['song__title', 'contributor', 'music_group']
        db_table = 'viewer_song_performance'
        constraints = [
            CheckConstraint(
                check=(
                        (Q(contributor__isnull=False) & Q(contributor_role__isnull=False) &
                         Q(music_group__isnull=True) & Q(music_group_role__isnull=True)) |
                        (Q(contributor__isnull=True) & Q(contributor_role__isnull=True) &
                         Q(music_group__isnull=False) & Q(music_group_role__isnull=False))
                ),
                name="contributor_or_group"
            )
        ]

    def display_more(self):
        album = self.song.albums.first()
        album_title = album.title if album else "Unknown Album"
        return f"{str(self)} ({album_title})"

    def __str__(self):
        if self.music_group:
            performer = self.music_group.name
        elif self.contributor:
            performer = str(self.contributor)
        else:
            performer = "Unknown Performer"

        return f"{performer} - {self.song}"

    def __repr__(self):
        return f"SongPerformance(song={self.song})"


class AlbumSong(Model):
    album = ForeignKey('Album', on_delete=CASCADE)
    song = ForeignKey('Song', on_delete=CASCADE)
    order = PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['album__title', 'order']
        db_table = 'viewer_album_song'
        # To implement later:
        # constraints = [
        #     UniqueConstraint(fields=['album', 'song'], name='unique_album_song'),
        #     UniqueConstraint(fields=['album', 'order'], name='unique_album_order'),
        # ]

    def __str__(self):
        return f"{self.album.title} - {self.order}. {self.song.title}"

    def __repr__(self):
        return f"<AlbumSong id={self.id} album={self.album_id} song={self.song_id} order={self.order}>"

class Album(Model):
    title = CharField(max_length=128)
    artist = ManyToManyField(Contributor, blank=True, related_name="albums")
    music_group = ManyToManyField(MusicGroup, blank=True, related_name="albums")
    songs = ManyToManyField(Song, through='AlbumSong', blank=True, related_name="albums")
    released = DateField(null=True, blank=True)
    summary = TextField(null=True, blank=True)
    cover_image = ImageField(upload_to='album_covers/', null=True, blank=True)

    class Meta:
        ordering = ['released', 'title']
        verbose_name = "Album"
        verbose_name_plural = "Albums"

    def songs_list(self):
        """Vrátí všechny songy na albu s prefetchem performances."""
        return self.songs.all().prefetch_related('performances')

    def ordered_songs(self):
        return Song.objects.filter(albumsong__album=self).order_by('albumsong__order')

    def total_duration(self):
        total = self.songs_list().aggregate(total=Sum('duration'))['total']
        return format_seconds(total) if total else None

    def genres_list(self):
        genre_ids = self.songs_list().values_list('genre', flat=True).distinct()
        return Genre.objects.filter(id__in=genre_ids).order_by('name')

    def languages_list(self):
        language_ids = self.songs_list().values_list('language', flat=True).distinct()
        return Language.objects.filter(id__in=language_ids).order_by('name')

    def contributors_by_category(self):
        all_performances = SongPerformance.objects.filter(song__in=self.songs_list()).select_related(
            'contributor', 'contributor_role', 'music_group', 'music_group_role'
        )

        contributors = {}
        for perf in all_performances:
            if perf.contributor and perf.contributor_role:
                cat = perf.contributor_role.category
                role_name = perf.contributor_role.name
                contributors.setdefault(cat, {})

                # pokud contributor není ještě v dictu, přidej ho s prázdným setem rolí
                if perf.contributor not in contributors[cat]:
                    contributors[cat][perf.contributor] = set()

                # přidej roli do setu rolí
                contributors[cat][perf.contributor].add(role_name)

        # převedeme sety rolí na seznamy a vytvoříme finální strukturu listů (contributor, [role_list])
        for cat, contribs in contributors.items():
            contributors[cat] = [(contrib, sorted(list(roles))) for contrib, roles in contribs.items()]

        return contributors

    def groups_by_role(self):
        all_performances = SongPerformance.objects.filter(song__in=self.songs_list()).select_related(
            'music_group', 'music_group_role'
        )
        groups = {}
        seen = set()
        for perf in all_performances:
            if perf.music_group and perf.music_group_role:
                role = perf.music_group_role.name
                groups.setdefault(role, [])
                if perf.music_group.id not in seen:
                    groups[role].append(perf.music_group)
                    seen.add(perf.music_group.id)
        return groups

    def display_creator(self):
        artist_names = ', '.join(str(artist) for artist in self.artist.all())
        group_names = ', '.join(group.name for group in self.music_group.all())

        if artist_names and group_names:
            creators = f"{artist_names} / {group_names}"
        else:
            creators = artist_names or group_names or "Unknown"

        return f"{creators}"

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"Album(title={self.title})"
