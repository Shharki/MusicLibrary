import datetime
from django.test import TestCase
from viewer.models import Genre, Country, Language, Contributor, ContributorRole, ContributorPreviousName, MusicGroup, \
    MusicGroupMembership, Song, SongPerformance, Album, AlbumSong


class MusicLibraryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):  # ZMĚNA: používáme cls. pro sdílené objekty
        cls.genre = Genre.objects.create(name="Pop")
        cls.country = Country.objects.create(name="Czech Republic")
        cls.language = Language.objects.create(name="Czech")

        cls.contributor = Contributor.objects.create(
            first_name="Karel",
            middle_name="",
            last_name="Gott",
            stage_name="Karel Gott",
            date_of_birth=datetime.date(1939, 7, 14),
            date_of_death=datetime.date(2019, 10, 1),
            country=cls.country,
            bio="Legendary Czech singer."
        )

        ContributorPreviousName.objects.create(
            contributor=cls.contributor,
            first_name="Karel",
            middle_name="",
            last_name="Hron"
        )

        cls.role = ContributorRole.objects.create(name="Singer")

        cls.group = MusicGroup.objects.create(
            name="Golden Kids",
            bio="Czech pop group",
            founded=datetime.date(1968, 1, 1),
            disbanded=datetime.date(1970, 12, 31)
        )

        membership = MusicGroupMembership.objects.create(
            member=cls.contributor,
            music_group=cls.group,
            from_date=datetime.date(1968, 1, 1),
            to_date=datetime.date(1970, 12, 31)
        )
        membership.member_role.set([cls.role])

        cls.song = Song.objects.create(
            title="Lady Carneval",
            duration=180,
            released=datetime.date(1969, 1, 1),
            summary="Popular Czech song",
            lyrics="La la la",
            language=cls.language
        )
        cls.song.genre.set([cls.genre])

        SongPerformance.objects.create(
            song=cls.song,
            contributor=cls.contributor,
            music_group=None,
            contributor_role=cls.role
        )

        cls.album = Album.objects.create(
            title="Zlatý hlas",
            released=datetime.date(1970, 1, 1),
            summary="Greatest hits"
        )

        AlbumSong.objects.create(
            album=cls.album,
            song=cls.song,
            order=1
        )

    def test_song_creation(self):
        self.assertEqual(self.song.released.year, 1969)  # ZMĚNA: použito self.song místo znovuvyhledávání
        self.assertEqual(self.song.genre.count(), 1)

    def test_contributor_str(self):
        self.assertEqual(str(self.contributor), "Karel Gott")

    def test_album_contains_song(self):
        self.assertIn(self.song, self.album.songs.all())

    def test_song_performance_contributor(self):
        performance = SongPerformance.objects.get(song=self.song)
        self.assertEqual(performance.contributor, self.contributor)

    def test_music_group_membership(self):
        membership = MusicGroupMembership.objects.get(member=self.contributor)
        self.assertEqual(membership.music_group.name, "Golden Kids")
        self.assertEqual(membership.member_role.first().name, "Singer")

    def test_song_language_name(self):
        self.assertEqual(self.song.language.name, "Czech")

    def test_song_format_seconds(self):
        self.assertEqual(self.song.format_seconds, "3:00")

    def test_contributor_previous_name(self):
        prev_name = ContributorPreviousName.objects.get(contributor=self.contributor)
        self.assertEqual(prev_name.last_name, "Hron")


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):  #  ZMĚNA: přesun vytvoření do setUpTestData
        cls.genre = Genre.objects.create(name="Rock")

    def test_str(self):
        self.assertEqual(str(self.genre), "Rock")


class CountryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="Czechia")

    def test_str(self):
        self.assertEqual(str(self.country), "Czechia")


class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Language.objects.create(name="English")

    def test_str(self):
        self.assertEqual(str(self.lang), "English")


class ContributorModelTest(TestCase):
    def test_str_with_stage_name(self):
        c = Contributor.objects.create(first_name="David", last_name="Bowie", stage_name="Ziggy")
        self.assertEqual(str(c), "Ziggy")

    def test_str_without_stage_name(self):
        c = Contributor.objects.create(first_name="John", last_name="Lennon")
        self.assertEqual(str(c), "John Lennon")


class ContributorRoleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.role = ContributorRole.objects.create(name="Singer")

    def test_str(self):
        self.assertEqual(str(self.role), "Singer")


class SongModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Language.objects.create(name="Czech")
        cls.song = Song.objects.create(title="Test Song", language=cls.lang)

    def test_str_and_repr(self):
        self.assertEqual(str(self.song), "Test Song")
        self.assertEqual(repr(self.song), "Song(title=Test Song)")
