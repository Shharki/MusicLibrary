from django.test import TestCase
from viewer.forms import GenreModelForm, CountryModelForm
from viewer.models import Genre, Country


class GenreModelFormTest(TestCase):

    def test_valid_genre_form(self):
        form = GenreModelForm(data={'name': 'Rock'})
        self.assertTrue(form.is_valid())
        genre = form.save()
        self.assertEqual(genre.name, 'Rock')

    def test_genre_name_is_capitalized(self):
        form = GenreModelForm(data={'name': 'jazz'})
        self.assertTrue(form.is_valid())
        genre = form.save()
        self.assertEqual(genre.name, 'Jazz')

    def test_genre_name_is_stripped(self):
        form = GenreModelForm(data={'name': '  blues  '})
        self.assertTrue(form.is_valid())
        genre = form.save()
        self.assertEqual(genre.name, 'Blues')

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

    def test_valid_country_form(self):
        form = CountryModelForm(data={'name': 'Germany'})
        self.assertTrue(form.is_valid())
        country = form.save()
        self.assertEqual(country.name, 'Germany')

    def test_country_name_is_capitalized_and_stripped(self):
        form = CountryModelForm(data={'name': '  slovakia  '})
        self.assertTrue(form.is_valid())
        country = form.save()
        self.assertEqual(country.name, 'Slovakia')

    def test_duplicate_country(self):
        Country.objects.create(name='Italy')
        form = CountryModelForm(data={'name': 'italy'})
        self.assertFalse(form.is_valid())
        self.assertIn('This country already exists.', form.errors['name'])