from datetime import date

from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from django.forms import DateField, NumberInput, CharField, Textarea

from accounts.models import Profile


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        #fields = '__all__'
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']

        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'E-mail',
            'password1': 'Password',
            'password2': 'Password again',
        }

    date_of_birth = DateField(
        widget=NumberInput(attrs={'type': 'date'}),
        label='Date of birth',
        required=False
    )

    biography = CharField(
        widget=Textarea,
        label='Biography',
        required=False
    )

    phone = CharField(
        label='Phone number',
        required=False
    )

    def clean_date_of_birth(self):
        initial = self.cleaned_data['date_of_birth']
        if initial and initial > date.today():
            raise ValidationError('Date of birth must not be in future.')
        return initial

    @atomic
    def save(self, commit=True):
        self.instance.is_active = True
        user = super().save(commit)  # User creation

        # Profile creation
        date_of_birth = self.cleaned_data.get('date_of_birth')
        biography = self.cleaned_data.get('biography')
        phone = self.cleaned_data.get('phone')
        profile = Profile(
            user=user,
            date_of_birth=date_of_birth,
            biography=biography,
            phone=phone
        )
        if commit:
            profile.save()
        return user