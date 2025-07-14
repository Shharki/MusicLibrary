from django.db.models import Model, CharField, DateField, ForeignKey, TextField, DateTimeField, SET_NULL, \
    ManyToManyField


class Genre(Model):
    name = CharField(max_length=64, null=False, blank=False, unique=True)

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


class Language(Model):
    name = CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Language(name={self.name})"


class Contributor(Model):
    first_name = CharField(max_length=64, null=False, blank=False)
    middle_name = CharField(max_length=64, null=True, blank=True)
    last_name = CharField(max_length=64, null=False, blank=False)
    stage_name = CharField(max_length=64, null=True, blank=True)
    date_of_birth = DateField(null=True, blank=True, unique=True)
    date_of_death = DateField(null=True, blank=True, unique=True)
    country = ForeignKey(Country, null=True, blank=True, on_delete=SET_NULL, related_name='contributors')
    bio = TextField(null=True, blank=True)


    class Meta:
        ordering = ['last_name', 'first_name']

    def __repr__(self):
        return f"Contributor({self.__str__()})"

    def __str__(self):
        return self.stage_name or f"{self.first_name} {self.last_name}"


class Group(Model):
    name = CharField(max_length=64, null=False, blank=False, unique=True)
    description = TextField(null=True, blank=True)
    date_of_establishment = DateField(null=True, blank=True, unique=True)
    termination = DateField(null=True, blank=True, unique=True)
    contributors = ManyToManyField(Contributor, related_name='groups')


    class Meta:
        ordering = ['name']

    def __repr__(self):
        return f"Group(name={self.name})"

    def __str__(self):
        return self.name

