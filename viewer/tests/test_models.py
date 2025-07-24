import datetime
from django.test import TestCase
from viewer.models import Genre, Country, Language, Contributor, ContributorRole, ContributorPreviousName, MusicGroup, \
    MusicGroupMembership, Song, SongPerformance, Album


class MusicLibraryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        genre = Genre.objects.create(name="Pop")
        country = Country.objects.create(name="Czech Republic")
        language = Language.objects.create(name="Czech")

        contributor = Contributor.objects.create(
            first_name="Karel",
            middle_name="",
            last_name="Gott",
            stage_name="Karel Gott",
            date_of_birth=datetime.date(1939, 7, 14),
            date_of_death=datetime.date(2019, 10, 1),
            country=country,
            bio="Legendary Czech singer."
        )

        ContributorPreviousName.objects.create(
            contributor=contributor,
            first_name="Karel",
            middle_name="",
            last_name="Hron"
        )

        role = ContributorRole.objects.create(name="Singer")

        group = MusicGroup.objects.create(
            name="Golden Kids",
            bio="Czech pop group",
            founded=datetime.date(1968, 1, 1),
            disbanded=datetime.date(1970, 12, 31)
        )

        membership = MusicGroupMembership.objects.create(
            member=contributor,
            music_group=group,
            from_date=datetime.date(1968, 1, 1),
            to_date=datetime.date(1970, 12, 31)
        )
        membership.member_role.set([role])

        song = Song.objects.create(
            title="Lady Carneval",
            duration=180,
            released_year=datetime.date(1969, 1, 1),
            summary="Popular Czech song",
            lyrics="La la la",
            language=language
        )
        song.genre.set([genre])

        SongPerformance.objects.create(
            song=song,
            contributor=contributor,
            music_group=None,
            contributor_role=role
        )

        album = Album.objects.create(
            title="Zlatý hlas",
            released_year=datetime.date(1970, 1, 1),
            summary="Greatest hits"
        )
        album.songs.set([song])

    def setUp(self):
        print('-' * 80)

    def test_song_creation(self):
        song = Song.objects.get(title="Lady Carneval")
        print(f"Test song creation name: {song.title}")
        self.assertEqual(song.released_year.year, 1969)
        self.assertEqual(song.genre.count(), 1)

    def test_contributor_str(self):
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        print(f"Test contributor string representation: {str(contributor)}")
        self.assertEqual(str(contributor), "Karel Gott")

    def test_album_contains_song(self):
        album = Album.objects.get(title="Zlatý hlas")
        song = Song.objects.get(title="Lady Carneval")
        print(f"Test album name: {album.title}")
        self.assertIn(song, album.songs.all())

    def test_song_performance_contributor(self):
        song = Song.objects.get(title="Lady Carneval")
        performance = SongPerformance.objects.get(song=song)
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        print(f"Test song name: {song.title}")
        self.assertEqual(performance.contributor, contributor)

    def test_music_group_membership(self):
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        membership = MusicGroupMembership.objects.get(member=contributor)
        print(f"Test music group name: {membership.music_group.name}")
        self.assertEqual(membership.music_group.name, "Golden Kids")
        self.assertEqual(membership.member_role.first().name, "Singer")

    def test_song_language_name(self):
        song = Song.objects.get(title="Lady Carneval")
        print(f"Song language name: {song.language.name}")
        self.assertEqual(song.language.name, "Czech")

    def test_song_duration_format(self):
        song = Song.objects.get(title="Lady Carneval")
        print(f"Song duration format: {song.duration_format}")
        self.assertEqual(song.duration_format(), "3:00")

    def test_contributor_previous_name(self):
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        prev_name = ContributorPreviousName.objects.get(contributor=contributor)
        print(f"Previous last name: {prev_name.last_name}")
        self.assertEqual(prev_name.last_name, "Hron")


class GenreModelTest(TestCase):
    def test_str(self):
        genre = Genre.objects.create(name="Rock")
        self.assertEqual(str(genre), "Rock")


class CountryModelTest(TestCase):
    def test_str(self):
        country = Country.objects.create(name="Czechia")
        self.assertEqual(str(country), "Czechia")


class LanguageModelTest(TestCase):
    def test_str(self):
        lang = Language.objects.create(name="English")
        self.assertEqual(str(lang), "English")


class ContributorModelTest(TestCase):

    def test_str_with_stage_name(self):
        c = Contributor.objects.create(first_name="David", last_name="Bowie", stage_name="Ziggy")
        self.assertEqual(str(c), "Ziggy")

    def test_str_without_stage_name(self):
        c = Contributor.objects.create(first_name="John", last_name="Lennon")
        self.assertEqual(str(c), "John Lennon")


class ContributorRoleModelTest(TestCase):
    def test_str(self):
        role = ContributorRole.objects.create(name="Singer")
        self.assertEqual(str(role), "Singer")


class SongModelTest(TestCase):
    def test_str_and_repr(self):
        lang = Language.objects.create(name="Czech")
        song = Song.objects.create(title="Test Song", language=lang)
        self.assertEqual(str(song), "Test Song")
        self.assertEqual(repr(song), "Song(title=Test Song)")