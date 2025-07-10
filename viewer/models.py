from django.db.models import Model, CharField, DateField, ForeignKey, TextField, DateTimeField, SET_NULL


class Genre(Model):
    name = CharField(max_length=32, null=False, blank=False, unique=True)

    class Meta:
        ordering = ['name']

    def __repr__(self):
        return f"Genre(name={self.name})"

    def __str__(self):
        return self.name


class Country(Model):
    name = CharField(max_length=64, null=False, blank=False, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'

    def __repr__(self):
        return f"Country(name={self.name})"

    def __str__(self):
        return self.name


class Artist(Model):
    name = CharField(max_length=32, null=True, blank=True)
    surname = CharField(max_length=32, null=True, blank=True)
    artistic_name = CharField(max_length=32, null=True, blank=True)
    date_of_birth = DateField(null=True, blank=True, unique=True)
    date_of_death = DateField(null=True, blank=True, unique=True)
    country = ForeignKey(Country, null=True, blank=True, on_delete=SET_NULL, related_name='artists')
    biography = TextField(null=True, blank=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)


    class Meta:
        ordering = ['surname', 'name']

    def __repr__(self):
        return f"Artist(name={self.name}, surname={self.surname})"

    def __str__(self):
        return self.artistic_name or f"{self.name} {self.surname}"

