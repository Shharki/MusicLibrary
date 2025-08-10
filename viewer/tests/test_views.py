import datetime
from django.contrib.auth.models import Permission, User
from django.test import TestCase, Client
from django.urls import reverse
from viewer.models import (
    Song, Language, Contributor, Country, Genre, ContributorRole, SongPerformance, AlbumSong,
    Album, MusicGroup, MusicGroupRole, MusicGroupMembership
)
from viewer.utils import format_seconds


class HomeViewTest(TestCase):
    def setUp(self):
        # Create some albums with and without cover images for testing get_queryset
        Album.objects.create(title="Album1", cover_image="")
        Album.objects.create(title="Album2")  # no cover image
        Album.objects.create(title="Album3", cover_image="covers/cover3.jpg")

    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_get_queryset_returns_only_albums_with_cover(self):
        response = self.client.get(reverse("home"))
        albums = response.context.get('albums', [])
        for album in albums:
            self.assertTrue(album.cover_image)
        self.assertLessEqual(len(albums), 6)


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
        # This text should be in your template if no songs exist
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
            released=datetime.date(1969, 1, 1),
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
        self.assertEqual(response.status_code, 200)

    def test_song_detail_contains_expected_data(self):
        song = Song.objects.get(title="Lady Carneval")
        contributor = Contributor.objects.get(stage_name="Karel Gott")
        response = self.client.get(reverse("song", args=[song.id]))
        self.assertContains(response, song.title)
        self.assertContains(response, str(contributor))
        self.assertContains(response, song.format_seconds)
        self.assertContains(response, str(song.released.year))


class ContributorListViewTest(TestCase):
    def test_contributors_list_view_empty(self):
        response = self.client.get(reverse('contributors'))
        self.assertEqual(response.status_code, 200)

        # Check context contains expected contributor categories
        self.assertIn('performers', response.context)
        self


class AlbumSongModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name="Czech Republic")
        cls.language = Language.objects.create(name="Czech")
        cls.genre = Genre.objects.create(name="Pop")
        cls.contributor = Contributor.objects.create(
            first_name="Karel",
            last_name="Gott",
            stage_name="Karel Gott",
            country=cls.country,
            date_of_birth=datetime.date(1939, 7, 14),
            date_of_death=datetime.date(2019, 10, 1)
        )
        cls.role = ContributorRole.objects.create(name="Singer", category="performer")

        cls.song = Song.objects.create(
            title="Lady Carneval",
            duration=180,
            released=datetime.date(1969, 1, 1),
            language=cls.language
        )
        cls.song.genre.set([cls.genre])

        cls.album = Album.objects.create(
            title="Zlatý hlas",
            released=datetime.date(1970, 1, 1),
            summary="Greatest hits"
        )

        cls.album_song = AlbumSong.objects.create(
            album=cls.album,
            song=cls.song,
            order=1
        )

    def test_album_song_creation(self):
        self.assertEqual(self.album_song.album, self.album)
        self.assertEqual(self.album_song.song, self.song)
        self.assertEqual(self.album_song.order, 1)

    def test_album_song_str(self):
        expected_str = f"{self.album.title} - {self.album_song.order}. {self.song.title}"
        self.assertEqual(str(self.album_song), expected_str)


class AlbumDetailViewTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Czech Republic")
        self.language = Language.objects.create(name="English")
        self.genre = Genre.objects.create(name="Rock")

        self.contributor = Contributor.objects.create(
            first_name="John", last_name="Doe", stage_name="JD",
            country=self.country, date_of_birth=datetime.date(1990, 1, 1)
        )
        self.role = ContributorRole.objects.create(name="Guitarist", category="performer")

        self.music_group = MusicGroup.objects.create(name="The Band")
        self.group_role = MusicGroupRole.objects.create(name="Band")

        self.song = Song.objects.create(
            title="Hit Song", duration=230, released=datetime.date(2020, 1, 1), language=self.language
        )
        self.song.genre.add(self.genre)

        SongPerformance.objects.create(song=self.song, contributor=self.contributor, contributor_role=self.role)
        SongPerformance.objects.create(song=self.song, music_group=self.music_group, music_group_role=self.group_role)

        self.album = Album.objects.create(title="Greatest Hits", released=datetime.date(2021, 1, 1))
        self.album.artist.add(self.contributor)
        self.album.music_group.add(self.music_group)

        AlbumSong.objects.create(album=self.album, song=self.song, order=1)

        MusicGroupMembership.objects.create(member=self.contributor, music_group=self.music_group)

    def test_album_detail_status_code_and_template(self):
        url = reverse('album', args=[self.album.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'album.html')

    def test_album_detail_contains_song_and_artist(self):
        url = reverse('album', args=[self.album.id])
        response = self.client.get(url)
        self.assertContains(response, self.album.title)
        self.assertContains(response, self.song.title)
        self.assertContains(response, str(self.contributor))
        self.assertContains(response, self.music_group.name)

    def test_total_duration_formatting(self):
        url = reverse('album', args=[self.album.id])
        response = self.client.get(url)
        expected_duration = format_seconds(self.song.duration)  # 230 seconds = 3:50
        self.assertEqual(response.context['total_duration'], expected_duration)


class MusicGroupsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group1 = MusicGroup.objects.create(
            name='The Rolling Codes',
            founded=datetime.date(2000, 1, 1),
            disbanded=datetime.date(2010, 1, 1),
            bio="Legendary Group of Decoders",
        )
        cls.group2 = MusicGroup.objects.create(
            name='Debuggers United',
            founded=datetime.date(2015, 5, 20),
            bio="Bugs, bugs, give them more bugs!",
        )

    def test_music_groups_view_status_code(self):
        response = self.client.get(reverse('music_groups'))
        self.assertEqual(response.status_code, 200)

    def test_music_groups_view_template_used(self):
        response = self.client.get(reverse('music_groups'))
        self.assertTemplateUsed(response, 'music-groups.html')

    def test_music_groups_context(self):
        response = self.client.get(reverse('music_groups'))
        self.assertIn('music_groups', response.context)
        self.assertEqual(len(response.context['music_groups']), 2)

    def test_music_groups_displayed_in_html(self):
        response = self.client.get(reverse('music_groups'))
        self.assertContains(response, 'The Rolling Codes')
        self.assertContains(response, 'Debuggers United')


class MusicGroupDetailViewTest(TestCase):
    def setUp(self):
        self.group = MusicGroup.objects.create(
            name="The Rolling Codes",
            bio="Legendární skupina vývojářů.",
            founded=datetime.date(2000, 1, 1),
            disbanded=datetime.date(2020, 1, 1)
        )

        self.member = Contributor.objects.create(
            first_name="Alan",
            last_name="Turing",
            stage_name="Code Wizard"
        )

        self.role = ContributorRole.objects.create(
            name="Lead Developer",
            category="performer"
        )

        membership = MusicGroupMembership.objects.create(
            member=self.member,
            music_group=self.group,
            from_date=datetime.date(2001, 1, 1),
            to_date=datetime.date(2010, 1, 1)
        )
        membership.member_role.add(self.role)

        self.album = Album.objects.create(
            title="Greatest Hits of Logic",
            released=datetime.date(2005, 6, 1)
        )
        self.album.music_group.add(self.group)

    def test_group_detail_view_status_code(self):
        url = reverse('music_group', args=[self.group.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_group_name_displayed(self):
        url = reverse('music_group', args=[self.group.pk])
        response = self.client.get(url)
        self.assertContains(response, self.group.name)

    def test_group_members_displayed(self):
        url = reverse('music_group', args=[self.group.pk])
        response = self.client.get(url)
        self.assertContains(response, self.member.stage_name)

    def test_group_albums_displayed(self):
        url = reverse('music_group', args=[self.group.pk])
        response = self.client.get(url)
        self.assertContains(response, self.album.title)


class SongsListViewTestSimple(TestCase):
    # This was duplicated, so renamed to avoid conflict.
    def test_view_renders_and_contains_expected_context(self):
        response = self.client.get(reverse('songs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('songs', response.context)
        self.assertEqual(response.context['model_name'], 'song')
        self.assertEqual(response.context['app_label'], 'viewer')


class SongDetailViewTestSimple(TestCase):
    def setUp(self):
        self.song = Song.objects.create(title="Test Song", duration=180)
        self.contributor = Contributor.objects.create(first_name="John", last_name="Doe")
        self.role = ContributorRole.objects.create(name="Singer", category="performer")
        SongPerformance.objects.create(song=self.song, contributor=self.contributor, contributor_role=self.role)

    def test_performances_grouped_correctly_in_context(self):
        response = self.client.get(reverse('song', kwargs={'pk': self.song.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('performances_by_category', response.context)
        self.assertIn('music_group_performances_by_role', response.context)
        self.assertIn('performer', response.context['performances_by_category'])
        self.assertTrue(len(response.context['performances_by_category']['performer']) > 0)


class SongCreateViewTest(TestCase):
    def test_redirect_if_no_permission(self):
        response = self.client.get(reverse('song_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login or no permission


class AlbumsListViewTest(TestCase):
    def setUp(self):
        for i in range(15):
            Album.objects.create(title=f"Album {chr(65 + i)}")

    def test_pagination_and_ordering(self):
        response = self.client.get(reverse('albums') + "?paginate_by=5&order=desc&letter=A")
        self.assertEqual(response.status_code, 200)
        albums = response.context['albums']
        for album in albums:
            self.assertTrue(album.title.startswith('A'))
        self.assertLessEqual(len(albums), 5)
        self.assertEqual(response.context['paginate_options'], [10, 20, 50, 100])
        self.assertIn('alphabet', response.context)




class AlbumCreateUpdateViewTest(TestCase):
    def setUp(self):
        self.song1 = Song.objects.create(title="Song1", duration=200)
        self.song2 = Song.objects.create(title="Song2", duration=180)

    def test_create_view_access(self):
        response = self.client.get(reverse('album_create'))
        self.assertEqual(response.status_code, 302)  # redirects to login

    def test_update_view_access(self):
        album = Album.objects.create(title="Test Album")
        response = self.client.get(reverse('album_update', kwargs={'pk': album.pk}))
        self.assertEqual(response.status_code, 302)  # redirects to login

class MusicGroupViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', 'user@example.com', 'pass')
        self.perm_user = User.objects.create_user('permuser', 'perm@example.com', 'pass')
        perm_add = Permission.objects.get(codename='add_musicgroup')
        self.perm_user.user_permissions.add(perm_add)
        self.group = MusicGroup.objects.create(name="Test Group")

    def test_music_groups_list_view(self):
        url = reverse('music_groups')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('music_groups', response.context)
        self.assertIn('alphabet', response.context)

    def test_music_group_detail_view(self):
        url = reverse('music_group', kwargs={'pk': self.group.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['music_group'], self.group)

    def test_music_group_create_view_permission(self):
        url = reverse('music_group_create')

        # Not logged in should redirect
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Logged in without permission => forbidden or redirect
        self.client.login(username='user', password='pass')
        response = self.client.get(url)
        self.assertIn(response.status_code, (302, 403))

        # Logged in with permission => OK
        self.client.login(username='permuser', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class MusicGroupRoleViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.role = MusicGroupRole.objects.create(name="Lead")
        self.user = User.objects.create_user('user', password='pass')
        self.perm_user = User.objects.create_user('permuser', password='pass')
        perm_add = Permission.objects.get(codename='add_musicgrouprole')
        self.perm_user.user_permissions.add(perm_add)

    def test_music_group_roles_list_view(self):
        url = reverse('music_group_roles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)

    def test_music_group_role_detail_view(self):
        url = reverse('music_group_role', kwargs={'pk': self.role.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('music_groups', response.context)

    def test_music_group_role_create_view_permission(self):
        url = reverse('music_group_role_create')

        # Not logged in => redirect
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Logged in with permission
        self.client.login(username='permuser', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class CountryViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(name="Testland")
        self.user = User.objects.create_user('user', password='pass')
        self.perm_user = User.objects.create_user('permuser', password='pass')
        perm_add = Permission.objects.get(codename='add_country')
        self.perm_user.user_permissions.add(perm_add)

    def test_countries_list_view(self):
        url = reverse('countries')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('countries', response.context)

    def test_country_create_view_permission(self):
        url = reverse('country_create')

        # Not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Logged in without permission
        self.client.login(username='user', password='pass')
        response = self.client.get(url)
        self.assertIn(response.status_code, (302, 403))

        # Logged in with permission
        self.client.logout()
        self.client.login(username='permuser', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class LanguageViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.language = Language.objects.create(name="English")
        self.user = User.objects.create_user('user', password='pass')
        self.perm_user = User.objects.create_user('permuser', password='pass')
        perm_add = Permission.objects.get(codename='add_language')
        self.perm_user.user_permissions.add(perm_add)

    def test_languages_list_view(self):
        url = reverse('languages')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('languages', response.context)

    def test_language_detail_view(self):
        url = reverse('language', kwargs={'pk': self.language.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('songs', response.context)

    def test_language_create_view_permission(self):
        url = reverse('language_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='permuser', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class GenreViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.genre = Genre.objects.create(name="Rock")
        self.user = User.objects.create_user('user', password='pass')
        self.perm_user = User.objects.create_user('permuser', password='pass')
        perm_add = Permission.objects.get(codename='add_genre')
        self.perm_user.user_permissions.add(perm_add)

    def test_genres_list_view(self):
        url = reverse('genres')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('genres', response.context)

    def test_genre_detail_view(self):
        url = reverse('genre', kwargs={'pk': self.genre.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('songs', response.context)

    def test_genre_create_view_permission(self):
        url = reverse('genre_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='permuser', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


from django.test import TestCase, Client
from django.urls import reverse
from viewer.models import Song, Album, Contributor

class SearchViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.song = Song.objects.create(title="Test Song")
        self.album = Album.objects.create(title="Test Album")
        self.contributor = Contributor.objects.create(first_name="John", last_name="Smith")

    def test_search_view_empty_query(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('query', ''), '')
        self.assertEqual(len(response.context.get('songs', [])), 0)
        self.assertEqual(len(response.context.get('external_songs', [])), 0)

    def test_search_view_with_query(self):
        response = self.client.get(reverse('search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.song, response.context.get('songs', []))
        self.assertIn('external_songs', response.context)


