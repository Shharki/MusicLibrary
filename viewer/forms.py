import re
from datetime import date

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, CharField, DateInput, DateField, ModelMultipleChoiceField, CheckboxSelectMultiple
from django.forms.widgets import Select, Textarea, SelectMultiple, ClearableFileInput, FileInput, NumberInput
from django.utils.timezone import now
from django.utils.safestring import mark_safe

from viewer.models import Genre, Country, Contributor, MusicGroup, Album, Song, Language, MusicGroupMembership, \
    ContributorRole, SongPerformance


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
        name = self.cleaned_data['name'].strip().title()
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

    def clean_name_field(self, field_value, field_label):
        if not field_value:
            return field_value
        field_value = field_value.strip().title()
        if not re.fullmatch(r'^[\w\d]+$', field_value): # Musí to být jedno slovo (bez mezer) a může obsahovat čísla
            raise ValidationError(f"{field_label} must be a single word and can include letters and digits only.")
        return field_value

    def clean_first_name(self):
        return self.clean_name_field(self.cleaned_data.get('first_name'), "First name")

    def clean_middle_name(self):
        return self.clean_name_field(self.cleaned_data.get('middle_name'), "Middle name")

    def clean_last_name(self):
        return self.clean_name_field(self.cleaned_data.get('last_name'), "Last name")

    def clean_stage_name(self):
        name = self.cleaned_data.get('stage_name')
        if name:
            name = name.strip().title()
            qs = Contributor.objects.filter(stage_name__iexact=name)
            # Pokud upravujeme existujícího přispěvatele, nepočítáme ho jako duplicitu
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("This stage name already exists.")
        return name

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if bio and len(bio.strip()) < 10:
            raise ValidationError("Biography must be at least 10 characters long.")
        return bio.strip()

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get('date_of_birth')
        date_of_death = cleaned_data.get('date_of_death')
        today = now().date()

        # Kontrola budoucích dat
        if date_of_birth and date_of_birth > today:
            self.add_error('date_of_birth', "Date of birth cannot be in the future.")

        if date_of_death and date_of_death > today:
            self.add_error('date_of_death', "Date of death cannot be in the future.")

        # Vzájemná kontrola data narození a úmrtí
        if date_of_birth and date_of_death:
            if date_of_birth > date_of_death:
                self.add_error('date_of_birth', "Date of birth cannot be after date of death.")
                self.add_error('date_of_death', "Date of death cannot be before date of birth.")


class MusicGroupModelForm(ModelForm):
    class Meta:
        model = MusicGroup
        fields = '__all__'
        labels = {
            'name': 'Group name',
            'bio': 'Biography',
            'founded': 'Founded date',
            'disbanded': 'Disbanded date',
            'country': 'Country of origin',
        }
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'bio': Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'founded': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'disbanded': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'country': Select(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip().title()
        qs = MusicGroup.objects.filter(name__iexact=name)
        if self.instance.pk:  # pokud existuje pk, tedy jde o editaci
            qs = qs.exclude(pk=self.instance.pk)  # vyřad ho z kontroly
        if qs.exists():
            raise ValidationError("This group already exists.")
        return name

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if bio:
            bio = bio.strip()
            if len(bio) < 10:
                raise ValidationError("Biography must be at least 10 characters long.")
        return bio

    def clean(self):
        cleaned_data = super().clean()
        founded = cleaned_data.get('founded')
        disbanded = cleaned_data.get('disbanded')
        today = now().date()

        if founded:
            if founded > today:
                self.add_error('founded', "Founded date cannot be in the future.")

        if disbanded:
            if disbanded > today:
                self.add_error('disbanded', "Disbanded date cannot be in the future.")

        if founded and disbanded:
            if founded > disbanded:
                raise ValidationError("Founded date cannot be after disbanded date.")


class MusicGroupPerformanceForm(ModelForm):
    class Meta:
        model = SongPerformance
        fields = ['song', 'music_group', 'music_group_role']  # pouze tyto 3 pole

    def clean(self):
        cleaned_data = super().clean()
        # Přidat validaci, že contributor a contributor_role jsou prázdné
        if cleaned_data.get('contributor') or cleaned_data.get('contributor_role'):
            raise ValidationError("Contributor fields must be empty when creating music group performance.")
        return cleaned_data


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
            if hasattr(image, 'content_type'):
                if image.content_type not in ['image/jpeg', 'image/png']:
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
        fields = [
            'title', 'artist', 'music_group', 'genre', 'duration',
            'released', 'summary', 'lyrics', 'language'
        ]
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'artist': SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'music_group': SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'genre': SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'duration': NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'released': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'summary': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lyrics': Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'language': Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Song Title',
            'artist': 'Artist(s)',
            'music_group': 'Music Group(s)',
            'genre': 'Genre(s)',
            'duration': 'Duration (in seconds)',
            'released': 'Release Date',
            'summary': 'Summary',
            'lyrics': 'Lyrics',
            'language': 'Language',
        }
        help_texts = {
            'duration': 'Duration of the song in seconds',
            'released': 'Release date of the song (optional)',
            'artist': mark_safe("Select one or more artists. "
                                '<strong>Do not add music group members as artists!</strong>'),
            'music_group': 'Select music groups',
            'genre': 'Select genres',
        }

        warnings = {
            'artist': 'If the song is by Music group, do not add the band members here!',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError("Song title is required.")
        if len(title) < 2:
            raise ValidationError("Title must be at least 2 characters long.")
        if len(title) > 100:
            raise ValidationError("Title is too long (max 100 characters).")
        if title.isupper():
            title = title.capitalize()
        else:
            # Capitalize each sentence
            title = re.sub(' +', ' ', title).strip().title()
        return title

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration is not None:
            if duration <= 0:
                raise ValidationError("Duration must be a positive number.")
            if duration > 60 * 60 * 10:  # e.g. max 10 hours (36000 seconds)
                raise ValidationError("Song duration is too long.")
        return duration

    def clean_released(self):
        released = self.cleaned_data.get('released')
        if released:
            if released > now().date():
                raise ValidationError("Release date cannot be in the future.")
            if released.year < 1800:
                raise ValidationError("Release date is too old.")
        return released

    def clean_summary(self):
        summary = self.cleaned_data.get('summary', '').strip()
        if summary and len(summary) < 10:
            raise ValidationError("Summary must be at least 10 characters long if provided.")
        return summary

    def clean_lyrics(self):
        lyrics = self.cleaned_data.get('lyrics', '').strip()

        if lyrics:
            if len(lyrics) < 10:
                raise ValidationError("Lyrics must be at least 10 characters long if provided.")

            if not re.search(r'[a-zA-Zá-žÁ-Ž]', lyrics):    # Regulární výraz: hledá aspoň jedno písmeno (a–z nebo A–Z, včetně českých znaků)
                raise ValidationError("Lyrics must contain at least one letter.")

        return lyrics

    def clean_language(self):
        language = self.cleaned_data.get('language')
        if language and not isinstance(language, Language):
            raise ValidationError("Invalid language")
        return language

    def clean_artist(self):
        artists = self.cleaned_data.get('artist')
        if artists and len(artists) > 10:
            raise ValidationError("You cannot select more than 10 artists.")
        return artists

    def clean_music_group(self):
        groups = self.cleaned_data.get('music_group')
        if groups and len(groups) > 5:
            raise ValidationError("You cannot select more than 5 music groups.")
        return groups

    def clean_genre(self):
        genres = self.cleaned_data.get('genre')
        if genres and len(genres) > 5:
            raise ValidationError("You cannot select more than 5 genres.")
        return genres

    def clean(self):
        cleaned_data = super().clean()
        artist = cleaned_data.get('artist')
        music_group = cleaned_data.get('music_group')
        # Validation: at least one artist or one music group must be selected
        if not artist and not music_group:
            raise ValidationError(
                "You must select at least one artist or one music group."
            )
        return cleaned_data


class MusicGroupMembershipForm(ModelForm):
    # member_role je M2M, tak použijeme widget s možností výběru více položek
    member_role = ModelMultipleChoiceField(
        queryset=ContributorRole.objects.all(),
        required=False,
        widget=CheckboxSelectMultiple,
        label="Roles"
    )

    class Meta:
        model = MusicGroupMembership
        fields = ['member', 'music_group', 'member_role', 'from_date', 'to_date']
        widgets = {
            'from_date': DateInput(attrs={'type': 'date'}),
            'to_date': DateInput(attrs={'type': 'date'}),
        }


class ContributorRoleForm(ModelForm):
    class Meta:
        model = ContributorRole
        fields = '__all__'


class ContributorSongPerformanceForm(ModelForm):
    class Meta:
        model = SongPerformance
        fields = ['song', 'contributor', 'contributor_role']  # pouze tyto 3 pole

    def clean(self):
        cleaned_data = super().clean()
        # Přidat validaci, že music_group a music_group_role jsou prázdné
        if cleaned_data.get('music_group') or cleaned_data.get('music_group_role'):
            raise ValidationError("Music group fields must be empty when creating contributor performance.")
        return cleaned_data


class SongPerformanceContributorForm(ModelForm):
    class Meta:
        model = SongPerformance
        fields = ['contributor', 'contributor_role']  # song se nastavuje mimo form

    def clean(self):
        cleaned_data = super().clean()

        music_group = cleaned_data.get('music_group')
        music_group_role = cleaned_data.get('music_group_role')
        if music_group or music_group_role:
            raise ValidationError("Music group fields must be empty for contributor performance.")

        contributor = cleaned_data.get('contributor')
        contributor_role = cleaned_data.get('contributor_role')

        song = self.initial.get('song') or getattr(self.instance, 'song', None)
        if not song:
            raise ValidationError("Song must be set before validation.")

        if contributor and contributor_role:
            qs = SongPerformance.objects.filter(
                song=song,
                contributor=contributor,
                contributor_role=contributor_role,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            print(f"Checking duplicates for contributor={contributor} role={contributor_role} song={song}")
            print(f"Instance PK: {self.instance.pk}")
            print(f"Duplicate count: {qs.count()}")

            if qs.exists():
                raise ValidationError("Tento contributor s touto rolí již existuje u této písně.")

        return cleaned_data


class SongPerformanceMusicGroupForm(ModelForm):
    class Meta:
        model = SongPerformance
        fields = ['music_group', 'music_group_role']  # bez 'song'

    def clean(self):
        cleaned_data = super().clean()

        # Contributor pole musí být prázdná
        if cleaned_data.get('contributor') or cleaned_data.get('contributor_role'):
            raise ValidationError("Contributor fields must be empty for music group performance.")

        music_group = cleaned_data.get('music_group')
        music_group_role = cleaned_data.get('music_group_role')
        song = self.initial.get('song') or getattr(self.instance, 'song', None)
        if not song:
            raise ValidationError("Song must be set before validation.")

        # ověření duplicity
        if music_group and music_group_role:
            qs = SongPerformance.objects.filter(
                song=song,
                music_group=music_group,
                music_group_role=music_group_role,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    "Tato music group s touto rolí už je v této písni zaznamenána."
                )

        return cleaned_data


class LanguageModelForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'
        labels = {
            'name': 'Language',
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
        name = self.cleaned_data['name'].strip()
        name = ' '.join(word.capitalize() for word in name.split())

        qs = Language.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("This language already exists.")
        return name

