from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *

from .forms import *

# mixin checking if user is logined and if he is an autor of modified record
class LoginAuthorMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        actual_object = self.get_object()
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user != actual_object.author:
            return render(request, 'not_allowed.html', {'title': "Nie masz uprawnień dla tej rodziny"})
        return super(LoginAuthorMixin, self).dispatch(request, *args, **kwargs)

# User management part

def user_allowed_families(user):
    families_list = user.families_set.all()
    return families_list


class AddUser(View):

    def get(self, request):
        form = UserCreateForm()
        return render(request, 'user.html', {'form':form})

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'user.html', {'form':form})
        return redirect('/login')

class ModUser(LoginRequiredMixin, View):

    login_url = '/login'

    def get(self, request):
        form = UserChangeForm()
        return render(request, 'user.html', {'form':form})

    def post(self, request):
        form = UserChangeForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/login')

# Management model Families

class ListFamilies(LoginRequiredMixin, ListView):

    login_url = '/login'
    template_name = 'families_list.html'

    # filtrowanie listy wyświetlanych rodzin do przypisanych
    def get_queryset(self):
        user = self.request.user
        queryset = user.families_set.all()
        return queryset
    # nadpisanie contextu ListView
    def get_context_data(self, **kwargs):
        context = super(ListFamilies, self).get_context_data(**kwargs)
        context['title'] = 'Lista rodzin'
        return context

    fields = ('name', 'description')

@login_required(login_url='/login')
def detail_family(request, family_id):

    if Families.objects.get(pk=family_id) not in user_allowed_families(request.user):
        return render(request, 'not_allowed.html', {'title': "Nie masz uprawnień dla tej rodziny"})

    family = Families.objects.get(pk=family_id)
    family_members = family.familymembers_set.all()
    ctx = {
        'family': family,
        'family_members': family_members
    }
    return render(request, 'family_detail.html', ctx)

class CreateFamily(LoginRequiredMixin, CreateView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Families
    fields = ('name', 'description')

    # nadpisanie contextu
    def get_context_data(self, **kwargs):
        context = super(CreateFamily, self).get_context_data(**kwargs)
        context['title'] = 'Formularz tworzenia rodziny'
        return context

    # dodanie dwóch pól wypełnianych automatycznie na podstawie zalogowanego usera
    def form_valid(self, form):
        self.object = form.save(commit=False)
        user = self.request.user

        self.object.author = user
        self.object.save()

        self.object.user.add(user) #relation many to many needs to be added after creating instance
        self.object.save()

        return super(CreateFamily, self).form_valid(form)

    success_url = '/'


class ModFamily(LoginAuthorMixin, UpdateView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Families
    fields = ('name', 'description', 'user')
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ModFamily, self).get_context_data(**kwargs)
        context['title'] = 'Modyfikujesz rodzinę {}'.format(self.object.name)
        return context


class DelFamily(LoginAuthorMixin, DeleteView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Families
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(DelFamily, self).get_context_data(**kwargs)
        context['title'] = 'Czy na pewno chcesz usunąć rodzinę {}?'.format(self.object.name)
        return context

# Management model Cities

class ListCities(LoginRequiredMixin, ListView):
    model = Cities
    login_url = '/login'
    template_name = 'cities_list.html'

    # nadpisanie contextu ListView
    def get_context_data(self, **kwargs):
        context = super(ListCities, self).get_context_data(**kwargs)
        context['title'] = 'Lista miast'
        return context
    fields = ('name', 'description')

# class ListAuthorCities(LoginRequiredMixin, ListView):
#     model = Cities
#     login_url = '/login'
#     template_name = 'cities_list.html'
#
#     # filtrowanie listy wyświetlanych elementów
#     def get_queryset(self):
#         user = self.request.user
#         queryset = user.cities_set.all()
#         return queryset
#     # nadpisanie contextu ListView
#     def get_context_data(self, **kwargs):
#         context = super(ListAuthorCities, self).get_context_data(**kwargs)
#         context['title'] = 'Lista utworzonych przez {} miast'.format(self.request.user.name)
#         return context
#
#     fields = ('name', 'description')