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
            contributor=contributor,
            music_group=group,
            from_date=datetime.date(1968, 1, 1),
            to_date=datetime.date(1970, 12, 31)
        )
        membership.contributor_role.set([role])

        song = Song.objects.create(
            title="Lady Carneval",
            duration=180,
            released_year=1969,
            summary="Popular Czech song",
            lyrics="La la la",
            language=language
        )
        song.genres.set([genre])

        SongPerformance.objects.create(
            song=song,
            contributor=contributor,
            music_group=None,
            contributor_role=role
        )

        album = Album.objects.create(
            title="Zlatý hlas",
            released_year=1970,
            summary="Greatest hits"
        )
        album.songs.set([song])

    def setUp(self):
        print('-' * 80)

    def test_song_creation(self):
        song = Song.objects.get(title="Lady Carneval")
        print(f"Test song creation name: {song.title}")
        self.assertEqual(song.released_year, 1969)
        self.assertEqual(song.genres.count(), 1)

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
        membership = MusicGroupMembership.objects.get(contributor=contributor)
        print(f"Test music group name: {membership.music_group.name}")
        self.assertEqual(membership.music_group.name, "Golden Kids")
        self.assertEqual(membership.contributor_role.first().name, "Singer")

    def test_song_language_name(self):
        song = Song.objects.get(title="Lady Carneval")
        print(f"Song language name: {song.language.name}")
        self.assertEqual(song.language.name, "Czech")

    def test_contributor_previous_name(self):
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        prev_name = ContributorPreviousName.objects.get(contributor=contributor)
        print(f"Previous last name: {prev_name.last_name}")
        self.assertEqual(prev_name.last_name, "Hron")
