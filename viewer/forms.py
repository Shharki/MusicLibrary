from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, CharField

from viewer.models import Genre, Country


class GenreModelForm(ModelForm):
    # Form for creating/editing Genre
    class Meta:
        model = Genre
        fields = '__all__'
        labels = {
            'name': 'Genre',
        }
        error_messages = {
            'name': {
                'required': 'This field is required.'
            }
        }
        widgets = {
            'name': TextInput(attrs={'class': 'bg-info'})
        }

    def clean_name(self):
        # Capitalize and check for duplicates
        name = self.cleaned_data['name'].strip().capitalize()
        if Genre.objects.filter(name__iexact=name).exists():
            raise ValidationError("This genre already exists.")
        return name


class CountryModelForm(ModelForm):
    class Meta:
        model = Country
        fields = '__all__'
        labels = {
            'name': 'Country',
        }
        error_messages = {
            'name': {
                'required': 'This field is required.'
            }
        }
        widgets = {
            'name': TextInput(attrs={'class': 'bg-info'})
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip().capitalize()
        if Country.objects.filter(name__iexact=name).exists():
            raise ValidationError("This country already exists.")
        return name