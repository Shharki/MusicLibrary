from django.test import TestCase
from viewer.forms import GenreModelForm
from viewer.models import Genre

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
