import re
from datetime import date

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, CharField, DateInput, DateField
from django.forms.widgets import Select, Textarea, SelectMultiple, ClearableFileInput, FileInput

from viewer.models import Genre, Country, Contributor, MusicGroup, Album, Song


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


class MusicGroupModelForm(ModelForm):
    class Meta:
        model = MusicGroup
        fields = '__all__'


class AlbumModelForm(ModelForm):
    released = DateField(
        required=False,
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Release date"
    )

    class Meta:
        model = Album
        fields = '__all__'

        labels = {
            'title': 'Album title',
            'artist': 'Artist(s)',
            'music_group': 'Music group(s)',
            'songs': 'Songs',
            'released': 'Release date',
            'summary': 'Summary',
            'cover_image': 'Album cover',
        }

        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'artist': SelectMultiple(attrs={'class': 'form-control'}),
            'music_group': SelectMultiple(attrs={'class': 'form-control'}),
            'songs': SelectMultiple(attrs={'class': 'form-control'}),
            'summary': Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cover_image': FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if not isinstance(visible.field.widget, FileInput):
                visible.field.widget.attrs['class'] = 'form-control'

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if not title:
            raise ValidationError("Album title is required.")
        title = title.strip()
        if len(title) < 2:
            raise ValidationError("Album title must be at least 2 characters long.")
        if title.isupper():
            title = title.capitalize()
        else:
            # Capitalize each sentence
            title = re.sub(' +', ' ', title).strip().title()
        return title

    def clean_released(self):
        released = self.cleaned_data.get('released')
        if released:
            if released > date.today():
                raise ValidationError("Release date cannot be in the future.")
            if released.year < 1880:
                raise ValidationError("Albums before 1880 are not supported.")
        return released

    def clean_summary(self):
        summary = self.cleaned_data.get('summary', '')
        if summary:
            summary = summary.strip()
            if len(summary) < 10:
                raise ValidationError("Summary must be at least 10 characters long.")
            summary = '. '.join(s.strip().capitalize() for s in re.split(r'[.!?]', summary) if s.strip())
        return summary

    def clean_cover_image(self):
        image = self.cleaned_data.get('cover_image')
        if image:
            if image.size > 2 * 1024 * 1024:
                raise ValidationError("Image file size must be under 2MB.")
            if not image.content_type in ['image/jpeg', 'image/png']:
                raise ValidationError("Only JPEG and PNG formats are supported.")
        return image

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        artists = cleaned_data.get('artist')
        groups = cleaned_data.get('music_group')
        songs = cleaned_data.get('songs')
        released = cleaned_data.get('released')

        errors = []

        if not artists and not groups:
            errors.append(ValidationError("At least one artist or music group must be selected."))

        if not songs or len(songs) == 0:
            errors.append(ValidationError("At least one song must be added to the album."))

        if title and (title.lower() == "untitled"):
            errors.append(ValidationError("Album title cannot be 'Untitled'."))

        if released and released.year > date.today().year:
            errors.append(ValidationError("Release year is invalid."))

        if errors:
            raise ValidationError(errors)

        return cleaned_data


class SongModelForm(ModelForm):
    class Meta:
        model = Song
        fields = '__all__'