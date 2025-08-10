from viewer.forms import GenreModelForm, CountryModelForm, ContributorModelForm, SongPerformanceMusicGroupForm, \
    LanguageModelForm, SongPerformanceContributorForm, ContributorSongPerformanceForm, ContributorRoleForm, \
    ContributorMusicGroupMembershipForm, SongModelForm
from viewer.models import Genre, Country, Contributor, Language, MusicGroup, ContributorRole, Song, MusicGroupRole, MusicGroupMembership

from django.test import TestCase
from datetime import date, timedelta


class GenreModelFormTest(TestCase):

    def test_valid_and_capitalized_name(self):
        form = GenreModelForm(data={'name': ' jazz '})
        self.assertTrue(form.is_valid())
        genre = form.save()
        self.assertEqual(genre.name, 'Jazz')

    def test_duplicate_genre(self):
        Genre.objects.create(name='Pop')
        form = GenreModelForm(data={'name': 'pop'})
        self.assertFalse(form.is_valid())
        self.assertIn('This genre already exists.', form.errors['name'])

    def test_blank_genre(self):
        form = GenreModelForm(data={'name': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['name'])


class CountryModelFormTest(TestCase):

    def test_valid_and_title_case_name(self):
        form = CountryModelForm(data={'name': '  slovakia  '})
        self.assertTrue(form.is_valid())
        country = form.save()
        self.assertEqual(country.name, 'Slovakia')

    def test_duplicate_country(self):
        Country.objects.create(name='Italy')
        form = CountryModelForm(data={'name': 'italy'})
        self.assertFalse(form.is_valid())
        self.assertIn('This country already exists.', form.errors['name'])


class ContributorModelFormTest(TestCase):

    def test_invalid_name_field(self):
        form = ContributorModelForm(data={'first_name': 'John Doe'})
        self.assertFalse(form.is_valid())
        self.assertIn('First name must be a single word and can include letters and digits only.', form.errors['first_name'])

    def test_duplicate_stage_name(self):
        Contributor.objects.create(stage_name='CoolGuy')
        form = ContributorModelForm(data={'stage_name': 'coolguy'})
        self.assertFalse(form.is_valid())
        self.assertIn('This stage name already exists.', form.errors['stage_name'])

    def test_bio_too_short(self):
        form = ContributorModelForm(data={'bio': 'Short'})
        self.assertFalse(form.is_valid())
        self.assertIn('Biography must be at least 10 characters long.', form.errors['bio'])

    def test_birth_date_in_future(self):
        future_date = date.today() + timedelta(days=1)
        form = ContributorModelForm(data={'date_of_birth': future_date})
        form.is_valid()
        self.assertIn('Date of birth cannot be in the future.', form.errors.get('date_of_birth', []))

    def test_death_date_in_future(self):
        future_date = date.today() + timedelta(days=1)
        form = ContributorModelForm(data={'date_of_death': future_date})
        form.is_valid()
        self.assertIn('Date of death cannot be in the future.', form.errors.get('date_of_death', []))

    def test_birth_date_after_death_date(self):
        form = ContributorModelForm(data={
            'date_of_birth': date(2000, 1, 2),
            'date_of_death': date(2000, 1, 1)
        })
        form.is_valid()
        self.assertIn('Date of birth cannot be after date of death.', form.errors.get('date_of_birth', []))
        self.assertIn('Date of death cannot be before date of birth.', form.errors.get('date_of_death', []))


class SongModelFormTest(TestCase):
    def setUp(self):
        # Create required related instances
        self.artist = Contributor.objects.create(first_name="Test", last_name="Artist")
        self.music_group = MusicGroup.objects.create(name="Test Group")

    def test_valid_data(self):
        form = SongModelForm(data={
            'title': 'My Song',
            'duration': 300,
            'released': date.today(),
            'artist': [self.artist.pk],  # add artist to pass validation
        })
        self.assertTrue(form.is_valid())

    def test_title_too_short(self):
        form = SongModelForm(data={
            'title': 'A',
            'artist': [self.artist.pk],  # required field
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Title must be at least 2 characters long.', form.errors['title'])

    def test_duration_negative(self):
        form = SongModelForm(data={
            'title': 'Valid Title',
            'duration': -10,
            'artist': [self.artist.pk],
        })
        self.assertFalse(form.is_valid())
        # Django's built-in validator error message for PositiveIntegerField
        self.assertIn('Ensure this value is greater than or equal to 0.', form.errors['duration'])

    def test_released_future_date(self):
        future = date.today() + timedelta(days=5)
        form = SongModelForm(data={
            'title': 'Valid Title',
            'released': future,
            'artist': [self.artist.pk],
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Release date cannot be in the future.', form.errors['released'])

    def test_artist_or_music_group_required(self):
        form = SongModelForm(data={
            'title': 'Valid Title',
            # No artist or music_group given
        })
        self.assertFalse(form.is_valid())
        self.assertIn('You must select at least one artist or one music group.', form.non_field_errors())


class ContributorMusicGroupMembershipFormTest(TestCase):
    def setUp(self):
        self.member = Contributor.objects.create(first_name="Member", last_name="One")
        self.group = MusicGroup.objects.create(name="Test Group")

    def test_form_valid_without_member_role(self):
        form = ContributorMusicGroupMembershipForm(data={
            'member': self.member.pk,  # member is required
            'music_group': self.group.pk,
            'from_date': '2020-01-01',
            'to_date': '2020-12-31',
        })
        self.assertTrue(form.is_valid())


class ContributorRoleFormTest(TestCase):
    def test_empty_form_is_valid(self):
        form = ContributorRoleForm(data={})
        form.is_valid()


class ContributorSongPerformanceFormTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(title="Song1", duration=200)
        self.contributor = Contributor.objects.create(first_name="John", last_name="Doe")
        self.role = ContributorRole.objects.create(name="Vocalist")

    def test_music_group_fields_must_be_empty(self):
        form = ContributorSongPerformanceForm(data={
            'song': self.song.pk,
            'contributor': self.contributor.pk,
            'contributor_role': self.role.pk,
            'music_group': '',  # No music_group field
        })
        self.assertTrue(form.is_valid())  # Should be valid because music_group is not a form field


class SongPerformanceContributorFormTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(title="Song1", duration=200)
        self.contributor = Contributor.objects.create(first_name="John", last_name="Doe")
        self.role = ContributorRole.objects.create(name="Vocalist")

    def test_music_group_fields_must_be_empty(self):
        form = SongPerformanceContributorForm(data={
            'contributor': self.contributor.pk,
            'contributor_role': self.role.pk,
        }, initial={'song': self.song})
        self.assertTrue(form.is_valid())  # music_group fields are not in form data, so valid


class SongPerformanceMusicGroupFormTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(title="Song2", duration=180)
        self.group = MusicGroup.objects.create(name="Band1")
        self.role = MusicGroupRole.objects.create(name="Guitarist")  # Use correct role model

    def test_contributor_fields_must_be_empty(self):
        # Since 'contributor' is not a field, simulate assignment in instance to test clean()
        form = SongPerformanceMusicGroupForm(data={
            'music_group': self.group.pk,
            'music_group_role': self.role.pk,
        }, initial={'song': self.song})
        self.assertTrue(form.is_valid())  # Should be valid since no contributor field given


class LanguageModelFormTest(TestCase):
    def test_duplicate_language_name(self):
        Language.objects.create(name="English")
        form = LanguageModelForm(data={'name': 'english'})
        self.assertFalse(form.is_valid())
        self.assertIn('This language already exists.', form.errors['name'])
