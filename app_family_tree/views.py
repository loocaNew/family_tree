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
            return render(request, 'not_allowed.html',
                          {'title': "Nie masz uprawnień do modyfikacji {}".format(actual_object.name)})
        return super(LoginAuthorMixin, self).dispatch(request, *args, **kwargs)

# User management part


def user_allowed_families(user):
    families_list = user.families_set.all()
    return families_list


def index(request):
    families = user_allowed_families(request.user)
    return render(request, 'index.html', {'families': families})


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
        form = UpdateProfile(instance=request.user)
        return render(request, 'user.html', {'form':form})

    def post(self, request):
        form = UpdateProfile(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/families')


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


@login_required(login_url='/login')
def detail_family(request, family_id):

    if Families.objects.get(pk=family_id) not in user_allowed_families(request.user):
        return render(request, 'not_allowed.html', {'title': "Nie masz uprawnień dla tej rodziny"})

    family = Families.objects.get(pk=family_id)
    persons = family.persons_set.all()
    ctx = {
        'family': family,
        'persons': persons
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

    success_url = '/families'


class ModFamily(LoginAuthorMixin, UpdateView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Families
    fields = ('name', 'description', 'user', 'senior')
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ModFamily, self).get_context_data(**kwargs)
        context['title'] = 'Modyfikujesz rodzinę {}'.format(self.object.name)
        return context


class DelFamily(LoginAuthorMixin, DeleteView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Families
    success_url = '/families'

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


@login_required(login_url='/login')
def detail_city(request, pk):
    city = Cities.objects.get(pk=pk)
    families = user_allowed_families(request.user)
    persons_birth = city.birth_city.all()
    persons_death = city.death_city.all()

    # for person in city.birth_city.all():
    #     if person.family in families:
    #         persons_birth = persons_birth | person
    #
    # for person in city.death_city.all():
    #     if person.family in families:
    #         persons_death = persons_death | person



    ctx = {
        'city': city,
        'persons_birth': persons_birth,
        'persons_death': persons_death
    }
    return render(request, 'city_detail.html', ctx)


class CreateCity(LoginRequiredMixin, CreateView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Cities
    fields = ('name', 'description')

    # nadpisanie contextu
    def get_context_data(self, **kwargs):
        context = super(CreateCity, self).get_context_data(**kwargs)
        context['title'] = 'Formularz tworzenia miasta'
        return context

    # dodanie pól wypełnianych automatycznie na podstawie zalogowanego usera
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super(CreateCity, self).form_valid(form)
    success_url = '/cities'


class ModCity(LoginAuthorMixin, UpdateView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Cities
    fields = ('name', 'description')
    success_url = '/cities'

    def get_context_data(self, **kwargs):
        context = super(ModCity, self).get_context_data(**kwargs)
        context['title'] = 'Modyfikujesz miasto {}'.format(self.object.name)
        return context


class DelCity(LoginAuthorMixin, DeleteView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Cities
    success_url = '/cities'

    def get_context_data(self, **kwargs):
        context = super(DelFamily, self).get_context_data(**kwargs)
        context['title'] = 'Czy na pewno chcesz usunąć miasto {}?'.format(self.object.name)
        return context


# Management model Persons


class ListPersons(LoginRequiredMixin, ListView):

    login_url = '/login'
    template_name = 'person_list.html'

    # nadpisanie contextu ListView
    def get_context_data(self, **kwargs):
        context = super(ListPersons, self).get_context_data(**kwargs)
        context['title'] = 'Lista członków rodzin'
        return context

    # filtrowanie listy wyświetlanych członków rodzin do przypisanych do rodziny
    def get_queryset(self):
        user = self.request.user
        queryset = user.families_set.all()
        return queryset

    fields = ('name', 'description')


class ListPersonsFamily(LoginRequiredMixin, ListView):

    model = Persons
    login_url = '/login'
    template_name = 'person_family_list.html'

    # nadpisanie contextu ListView
    def get_context_data(self, **kwargs):
        context = super(ListPersonsFamily, self).get_context_data(**kwargs)
        family = Families.objects.get(pk=self.kwargs.get('pk'))
        context['title'] = 'Lista członków rodziny'
        context['family'] = family
        if family not in self.request.user.families_set.all():
            context['error'] = 'Brak uprawnień do tej rodziny'
        else:
            context['error'] = 'Nie przypisano żadnych osób do tej rodziny'
        return context

    # filtrowanie listy wyświetlanych rodzin do przypisanych
    def get_queryset(self):
        family = Families.objects.get(pk=self.kwargs.get('pk'))
        if family not in self.request.user.families_set.all():
             queryset = Persons.objects.none()
        else:
             queryset = family.persons_set.all()
        return queryset
    fields = ('name', 'description')


@login_required(login_url='/login')
def detail_person(request, pk):
    person = Persons.objects.get(pk=pk)
    families = user_allowed_families(request.user)

    check = False
    for family in families:
        if person in family.persons_set.all():
            check=True
    if check == False:
        return render(request, 'not_allowed.html',
                      {'title': "Żądana osoba nie jest członkiem twoich rodzin"})
    ctx = {
        'person': person
    }
    return render(request, 'person_detail.html', ctx)


class CreatePerson(LoginRequiredMixin, CreateView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Persons
    fields = ('name',
              'surname',
              'description',
              'deceased',
              'sex',
              'birth_date',
              'birth_city',
              'death_date',
              'death_city',
              'siblings',
              'spouses',
              'parents',
              'family')

    # nadpisanie contextu
    def get_context_data(self, **kwargs):
        context = super(CreatePerson, self).get_context_data(**kwargs)
        context['title'] = 'Formularz tworzenia osoby'
        return context

    # dodanie pól wypełnianych automatycznie na podstawie zalogowanego usera
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super(CreatePerson, self).form_valid(form)

    success_url = '/persons'

class ModPerson(LoginAuthorMixin, UpdateView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Persons
    fields = ('name',
              'surname',
              'description',
              'deceased',
              'sex',
              'birth_date',
              'birth_city',
              'death_date',
              'death_city',
              'siblings',
              'spouses',
              'parents',
              'family')

    success_url = '/persons'

    def get_context_data(self, **kwargs):
        context = super(ModPerson, self).get_context_data(**kwargs)
        context['title'] = 'Modyfikujesz {} {}'.format(self.object.name, self.object.surname)
        return context

class DelPerson(LoginAuthorMixin, DeleteView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Persons
    success_url = '/persons'

    def get_context_data(self, **kwargs):
        context = super(DelPerson, self).get_context_data(**kwargs)
        context['title'] = 'Czy na pewno chcesz usunąć {} {}'.format(self.object.name, self.object.surname)
        return context

# Management model Stories
# Management model Photos

# List of objects where user is Author


class ListPersonsAuthor(LoginRequiredMixin, ListView):
    login_url = '/login'
    template_name = 'person_list_author.html'

    # nadpisanie contextu ListView
    def get_context_data(self, **kwargs):
        context = super(ListPersonsAuthor, self).get_context_data(**kwargs)
        context['title'] = 'Lista członków rodzin'
        return context

    # filtrowanie listy wyświetlanych członków rodzin do przypisanych do rodziny
    def get_queryset(self):
        user = self.request.user
        queryset = user.persons_set.all()
        return queryset


class ListCitiesAuthor(LoginRequiredMixin, ListView):
    model = Cities
    login_url = '/login'
    template_name = 'cities_list.html'

    # nadpisanie contextu ListView
    def get_context_data(self, **kwargs):
        context = super(ListCitiesAuthor, self).get_context_data(**kwargs)
        context['title'] = 'Lista miast stworzonych przez użytkownika'
        context['error'] = 'Brak miast stworzonych przez użytkownika'
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = user.cities_set.all()
        return queryset


class ListFamiliesAuthor(LoginRequiredMixin, ListView):
    login_url = '/login'
    template_name = 'families_list.html'

    # filtrowanie listy wyświetlanych rodzin do przypisanych
    def get_queryset(self):
        user = self.request.user
        queryset = user.author.all()
        return queryset

    # nadpisanie contextu ListView
    def get_context_data(self, **kwargs):
        context = super(ListFamiliesAuthor, self).get_context_data(**kwargs)
        context['title'] = 'Lista rodzin stworzonych przez użytkownika'
        return context

#algorytm z ustawionym seniorem rodu

# class TreeNode:
#     def __init__(self, id_, name):
#         self.id = id_
#         self.name = name
#         self.children = []
#
#     def __str__(self):
#         return "{}:{}".format(self.id, self.name)


def show_tree(node, level=0, d=None, parent=None):
    if d==None:
        d = {}
    if not len(d):
        d[level] = [['<ul class="sitemap">', '<li>', '<a href="/person/', node.pk, '">',
                     ' {} {}'.format(node.name, node.surname),'</a>', '</li>', '</ul>', parent.pk]]
    elif level in d:
        d[level].append(
            ['<ul>', '<li>', '<a href="/person/', node.pk, '">',
             ' {} {}'.format(node.name, node.surname),'</a>', '</li>', '</ul>', parent.pk])
    else:
        d[level] = [['<ul>', '<li>', '<a href="/person/', node.pk, '">',
                     ' {} {}'.format(node.name, node.surname),'</a>', '</li>', '</ul>', parent.pk]]
    if node.children.all():
        for element in node.children.all():
            show_tree(element, level + 1, d, node)

def showTree(node, level=0):
    print(node, level)
    if node.children.all():
        for element in node.children.all():
            showTree(element, level+1)

def family_tree(request, pk=None):
    families = request.user.families_set.all()

    if pk == None:
        pk = families[0].pk

    family = Families.objects.get(pk=pk)

    senior = family.senior
    d = {}
    show_tree(node=senior, d=d, parent=senior)
    # print(len(d))
    # print(d[0])
    # print(d[1])
    # print(d[2])
    # print(d[3])

    # print(d)
    new_list = []
    new_list.extend(d[0][0][:-1])
    # print(new_list)
    for j in range(1, len(d)): #len(d)
        list_temp = []
        for i in range(len(d[j])):
            if i == 0:
                list_temp.extend(d[j][i][:-2])  #initial list node creation (wihout ending /ul)
                # print(list_temp)
                if i == (len(d[j])-1):
                    parent_node = d[j][i][-1]
                    # print(parent_node)
                    list_temp.append('</ul>')
                    # print(list_temp)
                    idx = new_list.index(parent_node) + 4
                    new_list[idx:idx] = list_temp
                    list_temp = []
            elif d[j][i][-1] == d[j][i-1][-1]:
                list_temp.extend(d[j][i][1:-2])
                # print(list_temp)
                if i == (len(d[j])-1):
                    parent_node = d[j][i][-1]
                    # print(parent_node)
                    list_temp.append('</ul>')
                    # print(list_temp)
                    idx = new_list.index(parent_node) + 4
                    new_list[idx:idx] = list_temp
                    list_temp = []
            else:
                parent_node = d[j][i-1][-1]
                # print(parent_node)
                idx = new_list.index(parent_node) + 4
                list_temp.append('</ul>')
                # print(list_temp)
                new_list[idx:idx] = list_temp
                list_temp = []
                list_temp.extend(d[j][i][:-2])
                if i == (len(d[j])-1):
                    parent_node = d[j][i][-1]
                    # print(parent_node)
                    idx = new_list.index(parent_node) + 4
                    new_list[idx:idx] = list_temp
                    list_temp = []

    final = []
    for element in new_list:
        final.append(str(element))
    ctx={
        'list':''.join(final),
        'families':families,
        'family':family
    }
    print(family.name)

    return render(request, 'test.html', ctx)


# def family_tree (request, pk):
#
#     family = Families.objects.get(pk=pk)
#     persons = family.persons_set.all()
#     senior = family.senior
#
#     tree_map = [{
#         'node':0,
#         'element_id':0
#         'node_elements':0
#         'children':[],
#         'spouses':[]
#     }]
#
#
#     object = senior
#     i = 1
#
#
#     while check:
#         check = False
#         if i == 1:
#             tree_map[i - 1]['node'] = i
#             tree_map[i - 1]['node_elements'] = len(object.children.all())
#             tree_map[i - 1]['element_id'] = object.pk
#             for child in object.children.all():
#                 tree_map[i-1].['children'].append(child.pk)
#             for spouse in object.spouses.all():
#                 tree_map[i-1].['spouses'].append(spouse.pk)
#             for spouse in object.spouses_set.all():
#                 tree_map[i-1].['spouses'].append(spouse.pk)
#             i += 1
#         else:
#             for child in persons.get.(pk=tree_map[i-2]['element_id']):
#                 tree_map[i - 1]['node'] = i
#                 if not tree_map[i - 1]['node_elements']:
#                     tree_map[i - 1]['node_elements'] = len(object.children.all())
#
#                 tree_map[i - 1]['element_id'] = object.pk