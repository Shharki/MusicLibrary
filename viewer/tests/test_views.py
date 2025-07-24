import datetime

from django.test import TestCase
from django.urls import reverse
from viewer.models import Song, Language, Contributor, Country, Genre, ContributorRole, SongPerformance


class HomeViewTest(TestCase):
    def test_home_page_status_code_and_content(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to the music database MusicLibrary")


class SongsListViewTest(TestCase):
    def test_songs_view_with_songs(self):
        lang = Language.objects.create(name="English")
        Song.objects.create(title="Imagine", language=lang)
        response = self.client.get(reverse("songs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Imagine")

    def test_songs_view_no_songs(self):
        response = self.client.get(reverse("songs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There is no song in the database.")


class SongDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        country = Country.objects.create(name="Czech Republic")
        language = Language.objects.create(name="Czech")
        contributor = Contributor.objects.create(
            first_name="Karel",
            last_name="Gott",
            stage_name="Karel Gott",
            country=country,
            date_of_birth=datetime.date(1939, 7, 14),
            date_of_death=datetime.date(2019, 10, 1)
        )
        genre = Genre.objects.create(name="Pop")
        role = ContributorRole.objects.create(name="Singer")
        song = Song.objects.create(
            title="Lady Carneval",
            duration=180,
            released_year=datetime.date(1969, 1, 1),
            language=language
        )
        song.genre.set([genre])
        SongPerformance.objects.create(
            song=song,
            contributor=contributor,
            contributor_role=role
        )

    def test_song_detail_view_status_code(self):
        song = Song.objects.get(title="Lady Carneval")
        url = reverse("song", args=[song.id])
        response = self.client.get(url)
        print(f"[song] Status Code for URL '{url}': {response.status_code}")
        self.assertEqual(response.status_code, 200)

    def test_song_detail_view_contains_title(self):
        song = Song.objects.get(title="Lady Carneval")
        response = self.client.get(reverse("song", args=[song.id]))
        print(f"[song] Checking if title '{song.title}' is in response")
        self.assertContains(response, song.title)

    def test_song_detail_view_contains_contributor(self):
        song = Song.objects.get(title="Lady Carneval")
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        response = self.client.get(reverse("song", args=[song.id]))
        print(f"[song] Looking for contributor '{contributor}'")
        self.assertContains(response, str(contributor))

    def test_song_detail_view_contains_duration(self):
        song = Song.objects.get(title="Lady Carneval")
        response = self.client.get(reverse("song", args=[song.id]))
        print(f"[song] Checking for formatted duration: {song.duration_format()}")
        self.assertContains(response, song.duration_format())

    def test_song_detail_view_contains_released_year(self):
        song = Song.objects.get(title="Lady Carneval")
        response = self.client.get(reverse("song", args=[song.id]))
        released_year = song.released_year.year
        print(f"[song] Checking for released year: {released_year}")
        self.assertContains(response, str(released_year))


class ContributorListViewTest(TestCase):
    def test_contributors_list_view_status_code(self):
        response = self.client.get(reverse('contributors'))
        self.assertEqual(response.status_code, 200)

    def test_contributors_list_view_uses_correct_template(self):
        response = self.client.get(reverse('contributors'))
        self.assertTemplateUsed(response, 'contributors.html')

    def test_contributors_list_view_context_with_data(self):
        Contributor.objects.create(first_name="Karel", last_name="Gott")
        response = self.client.get(reverse('contributors'))
        self.assertIn('contributors', response.context)
        self.assertContains(response, "Karel")
        self.assertContains(response, "Gott")

    def test_contributors_list_view_context_empty(self):
        response = self.client.get(reverse('contributors'))
        self.assertIn('contributors', response.context)
        self.assertContains(response, "There is no contributor in the database.")

