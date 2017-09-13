from django.contrib.auth.models import User
from django.db import models
from django.contrib.admin import ModelAdmin
# Create your models here.

class Families(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    user = models.ManyToManyField(User)
    author = models.ForeignKey(User, related_name='author')
    senior = models.OneToOneField('Persons', related_name='senior', blank=True, null=True)

    def __str__(self):
        return self.name

class Cities(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    author = models.ForeignKey(User)

    def __str__(self):
        return self.name

LIVING = (
    (0, 'living'),
    (1, 'deceased')
)

SEX = (
    (0, 'male'),
    (1, 'female')
)

class Persons(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    description = models.TextField()
    deceased = models.BooleanField(choices=LIVING, default=0, verbose_name="deceased or living")
    sex = models.BooleanField(choices=SEX, default=0, verbose_name="gender")
    birth_date = models.DateField(blank=True, null=True, verbose_name="date of birth")
    birth_city = models.ForeignKey('Cities', related_name='birth_city',
                                   verbose_name='city of birth', blank=True, null=True)
    death_date = models.DateField(blank=True, null=True, verbose_name="date of death")
    death_city = models.ForeignKey('Cities', related_name='death_city',
                                   verbose_name='city of death', blank=True, null=True)
    siblings = models.ManyToManyField('Persons', related_name='siblings_set', blank=True)
    spouses = models.ManyToManyField('Persons', related_name='spouses_set', blank=True)
    parents = models.ManyToManyField('Persons', related_name='children', blank=True)
    family = models.ManyToManyField('Families')
    author = models.ForeignKey(User)

    def __str__(self):
        return '{} {}'.format(self.name, self.surname)


class Photos(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    path = models.CharField(max_length=256)
    family = models.ForeignKey('Families', blank=True, null=True)
    city = models.ForeignKey('Cities', blank=True, null=True)
    person = models.ManyToManyField('Persons', blank=True)
    author = models.ForeignKey(User)

    def __str__(self):
        return self.name

class Stories(models.Model):
    name = models.CharField(max_length=256)
    content = models.TextField()
    family = models.ForeignKey('Families', blank=True, null=True)
    city = models.ForeignKey('Cities', blank=True, null=True)
    person = models.ManyToManyField('Persons', blank=True)
    author = models.ForeignKey(User)


