from django.contrib import admin
from .models import Families, Cities, Persons, Photos, Stories

# Register your models here.

admin.site.register([Families, Cities, Persons, Photos, Stories])

#list_filter
#list_search
