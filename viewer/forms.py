from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, CharField, DateInput
from django.forms.widgets import Select, Textarea

from viewer.models import Genre, Country, Contributor


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


class ContributorModelForm(ModelForm):
    class Meta:
        model = Contributor
        fields = '__all__'
        labels = {
            'first_name': 'First name',
            'middle_name': 'Middle name',
            'last_name': 'Last name',
            'stage_name': 'Stage name',
            'date_of_birth': 'Date of birth',
            'date_of_death': 'Date of death',
            'country': 'Country',
            'bio': 'Biography',
        }
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'middle_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'stage_name': TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_death': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'country': Select(attrs={'class': 'form-control'}),
            'bio': Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_stage_name(self):
        name = self.cleaned_data.get('stage_name')
        if name:
            name = name.strip()
            if Contributor.objects.filter(stage_name__iexact=name).exists():
                raise ValidationError("This stage name already exists.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        death_date = cleaned_data.get('death_date')

        if birth_date and death_date and birth_date > death_date:
            raise ValidationError("Date of birth cannot be after date of death.")