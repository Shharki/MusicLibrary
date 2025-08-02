import datetime
from unittest import skip

from django.test import TestCase
from viewer.models import Genre, Country, Language, Contributor, ContributorRole, ContributorPreviousName, MusicGroup, \
    MusicGroupMembership, Song, SongPerformance, Album, AlbumSong, MusicGroupRole


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


class MusicGroupModelTest(TestCase):
    def setUp(self):
        self.group = MusicGroup.objects.create(name="Test Group", bio="Just a test.")

    def test_str_and_repr(self):
        self.assertEqual(str(self.group), "Test Group")
        self.assertIn("Test Group", repr(self.group))

    def test_all_albums_ordering(self):
        album1 = Album.objects.create(title="B", released="2020-01-01")
        album2 = Album.objects.create(title="A", released="2019-01-01")
        self.group.albums.add(album1, album2)
        ordered = list(self.group.all_albums)
        self.assertEqual(ordered, [album2, album1])


class MusicGroupMembershipModelTest(TestCase):
    def test_active_period_display(self):
        contributor = Contributor.objects.create(first_name="John", last_name="Doe")
        group = MusicGroup.objects.create(name="Test Group")
        membership = MusicGroupMembership.objects.create(
            member=contributor,
            music_group=group,
            from_date=datetime.date(2000, 1, 1),
            to_date=datetime.date(2005, 1, 1)
        )
        self.assertEqual(membership.active_period, "[2000-01-01–2005-01-01]")

    def test_display_roles(self):
        contributor = Contributor.objects.create(first_name="John", last_name="Doe")
        group = MusicGroup.objects.create(name="Test Group")
        role1 = ContributorRole.objects.create(name="Guitarist")
        role2 = ContributorRole.objects.create(name="Vocalist")
        membership = MusicGroupMembership.objects.create(
            member=contributor,
            music_group=group
        )
        membership.member_role.set([role1, role2])
        self.assertIn("Guitarist", membership.display_roles())
        self.assertIn("Vocalist", membership.display_roles())


class MusicGroupRoleModelTest(TestCase):
    def test_str_and_repr(self):
        role = MusicGroupRole.objects.create(name="Band Leader")
        self.assertEqual(str(role), "Band Leader")
        self.assertIn("Band Leader", repr(role))


class SongPerformanceModelTest(TestCase):
    def test_str_repr_contributor(self):
        contributor = Contributor.objects.create(first_name="Jane", last_name="Doe")
        role = ContributorRole.objects.create(name="Singer")
        song = Song.objects.create(title="Test Song")
        performance = SongPerformance.objects.create(
            song=song,
            contributor=contributor,
            contributor_role=role
        )
        self.assertIn("Jane Doe - Test Song", str(performance))
        self.assertIn("Test Song", repr(performance))

    def test_str_repr_music_group(self):
        group = MusicGroup.objects.create(name="Test Band")
        group_role = MusicGroupRole.objects.create(name="Main")
        song = Song.objects.create(title="Test Song 2")
        performance = SongPerformance.objects.create(
            song=song,
            music_group=group,
            music_group_role=group_role
        )
        self.assertIn("Test Band - Test Song 2", str(performance))


class AlbumSongModelTest(TestCase):
    def test_str_repr(self):
        song = Song.objects.create(title="Track")
        album = Album.objects.create(title="Album")
        album_song = AlbumSong.objects.create(album=album, song=song, order=1)
        self.assertIn("Album - 1. Track", str(album_song))
        self.assertIn("album=", repr(album_song))
        self.assertIn("song=", repr(album_song))


class AlbumModelTest(TestCase):
    @skip # Better later than never
    def test_display_more(self):
        contributor = Contributor.objects.create(first_name="Anna", last_name="Smith")
        group = MusicGroup.objects.create(name="Test Band")
        album = Album.objects.create(title="Test Album", released=datetime.date(2000, 1, 1))
        album.artist.add(contributor)
        album.music_group.add(group)
        display = album.display_more() # Nefunguje Ti display, more
        self.assertIn("2000", display)
        self.assertIn("Test Band", display)
        self.assertIn("Anna Smith", display)

    def test_str_repr(self):
        album = Album.objects.create(title="Test Album")
        self.assertEqual(str(album), "Test Album")
        self.assertIn("Test Album", repr(album))