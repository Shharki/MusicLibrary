import datetime
from django.test import TestCase
from viewer.models import Genre, Country, Language, Contributor, ContributorRole, ContributorPreviousName, MusicGroup, \
    MusicGroupMembership, Song, SongPerformance, Album


class MusicLibraryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre = Genre.objects.create(name="Pop")
        cls.country = Country.objects.create(name="Czech Republic")
        cls.language = Language.objects.create(name="Czech")

        cls.contributor = Contributor.objects.create(
            first_name="Karel",
            middle_name="",
            last_name="Gott",
            stage_name="Karel Gott",
            date_of_birth=datetime.date(1939, 7, 14),
            date_of_death=datetime.date(1919, 10, 1),
            country=cls.country,
            bio="Legendary Czech Singer"
        )

        cls.previous_name = ContributorPreviousName.objects.create(
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

        cls.membership = MusicGroupMembership.objects.create(
            contributor=cls.contributor,
            music_group=cls.group,
            from_date=datetime.date(1968, 1, 1),
            to_date=datetime.date(1970, 12, 31)
        )

        cls.membership.role.set([cls.role])

        cls.song = Song.objects.create(
            title="Lady Carneval",
            duration=180,
            released_year=1969,
            summary="Popular Czech song",
            lyrics="La La La",
            language=cls.language,
        )
        cls.song.genres.set([cls.genre])

        cls.performance = SongPerformance.objects.create(
            song=cls.song,
            contributor=cls.contributor,
            music_group=None,
            role=cls.role,
        )

        cls.album = Album.objects.create(
            title="Zlatý hlas",
            released_year=1970,
            summary="Greatest hits"
        )
        cls.album.songs.set([cls.song])

    def test_song_creation(self):
        self.assertEqual(Song.objects.count(), 1)
        song = Song.objects.get(title="Lady Carneval")
        self.assertEqual(song.released_year, 1969)
        self.assertIn(self.genre, song.genres.all())

    def test_contributor_str(self):
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        self.assertEqual(str(contributor), "Karel Gott")

    def test_album_contains_song(self):
        album = Album.objects.get(title="Zlatý hlas")
        self.assertIn(self.song, album.songs.all())

    def test_song_performance_link(self):
        performance = SongPerformance.objects.get(song=self.song)
        self.assertEqual(performance.contributor, self.contributor)

    def test_music_group_membership(self):
        membership = MusicGroupMembership.objects.get(contributor=self.contributor)
        self.assertEqual(membership.music_group.name, "Golden Kids")
        self.assertIn(self.role, membership.role.all())

    def test_language_link(self):
        song = Song.objects.get(title="Lady Carneval")
        self.assertEqual(song.language.name, "Czech")

    def test_contributor_previous_name(self):
        prev_name = ContributorPreviousName.objects.get(contributor=self.contributor)
        self.assertEqual(prev_name.last_name, "Hron")


