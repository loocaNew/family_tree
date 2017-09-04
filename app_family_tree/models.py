from django.contrib.auth.models import User
from django.db import models
# Create your models here.

class Families(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    user = models.ManyToManyField(User)
    author = models.ForeignKey(User, related_name='author')

    def __str__(self):
        return self.name

class Cities(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    author = models.ForeignKey(User)

    def __str__(self):
        return self.name


class FamilyMembers(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    description = models.TextField()
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    siblings = models.ManyToManyField('FamilyMembers', related_name='siblings_set', blank=True)
    parents = models.ManyToManyField('FamilyMembers', related_name='children', blank=True)
    birth_city = models.OneToOneField('Cities', related_name='birth_city', blank=True, null=True)
    death_city = models.OneToOneField('Cities', related_name='death_city', blank=True, null=True)
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
    family_member = models.ManyToManyField('FamilyMembers', blank=True)
    author = models.ForeignKey(User)

    def __str__(self):
        return self.name

class Stories(models.Model):
    name = models.CharField(max_length=256)
    content = models.TextField()
    family = models.ForeignKey('Families', blank=True, null=True)
    city = models.ForeignKey('Cities', blank=True, null=True)
    family_member = models.ManyToManyField('FamilyMembers', blank=True)
    author = models.ForeignKey(User)