from django.test import TestCase
from django.urls import reverse
from viewer.models import Song, Language


class HomeViewTest(TestCase):
    def test_home_page_status_code_and_content(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to music database MusicLibrary.")


class SongsViewTest(TestCase):
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