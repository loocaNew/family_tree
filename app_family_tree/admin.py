from django.contrib import admin
from .models import Families, Cities, FamilyMembers, Photos, Stories

# Register your models here.

admin.site.register([Families, Cities, FamilyMembers, Photos, Stories])

#list_filter
#list_search
