"""family_tree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views
from app_family_tree.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', ListFamilies.as_view(), name='index'),

    #User management part
    url(r'^login/?$', views.login, {'template_name':'registration/login1.html'}, name='login'),
    url(r'^logout/?$', views.logout_then_login, name='logout'),
    url(r'^pass_change/?$', views.password_change, {'post_change_redirect':'/families'},  name='pass_change'),
    url(r'^user/add$', AddUser.as_view(), name='user_add'),
    url(r'^user/mod$', ModUser.as_view(), name='user_mod'),


    #Families management part
    url(r'^families$', ListFamilies.as_view(), name='families_list'),
    url(r'^family/(?P<family_id>(\d)+)$', detail_family, name='family_detail'),
    url(r'^family/add$', CreateFamily.as_view(), name='create_family'),
    url(r'^family/mod/(?P<pk>(\d)+)$', ModFamily.as_view(), name='modify_family'),
    url(r'^family/del/(?P<pk>(\d)+)$', DelFamily.as_view(), name='delete_family'),

    #Cities management part
    url(r'^cities/?$', ListCities.as_view(), name='cities_list'),
    # url(r'^cities/author$', ListAuthorCities.as_view(), name='cities_author_list'),
    url(r'^city/(?P<pk>(\d)+)$', detail_city, name='city_detail'),
    url(r'^city/add$', CreateCity.as_view(), name='create_city'),
    url(r'^city/mod/(?P<pk>(\d)+)$', ModCity.as_view(), name='modify_city'),
    url(r'^city/del/(?P<pk>(\d)+)$', DelCity.as_view(), name='delete_city'),

    # Persons management part
    url(r'^persons/?$', ListPersons.as_view(), name='persons_list'),
    url(r'^persons/family/(?P<pk>(\d)+)$', ListPersonsFamily.as_view(), name='persons_family_list'),
    # url(r'^cities/author$', ListAuthorCities.as_view(), name='cities_author_list'),
    url(r'^person/(?P<pk>(\d)+)$', detail_person, name='person_detail'),
    url(r'^person/add$', CreatePerson.as_view(), name='create_person'),
    url(r'^person/mod/(?P<pk>(\d)+)$', ModPerson.as_view(), name='modify_person'),
    url(r'^person/del/(?P<pk>(\d)+)$', DelPerson.as_view(), name='delete_person'),
    # Administration part
    url(r'^persons/admin$', ListPersonsAuthor.as_view(), name='persons_author_list'),
    url(r'^cities/admin$', ListCitiesAuthor.as_view(), name='cities_author_list'),
    url(r'^families/admin$', ListFamiliesAuthor.as_view(), name='families_author_list'),
    # Tree view part
    url(r'^tree/?$', family_tree, name='tree_init'),
    url(r'^tree/(?P<pk>(\d)+)$', family_tree, name='tree'),

    #test part
    url(r'^test/?$', render_test, name='test'),
]

