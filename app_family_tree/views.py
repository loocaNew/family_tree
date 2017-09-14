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

def allowed_persons(request):
    all_families = request.user.families_set.all()
    all_persons = Persons.objects.filter(family__in=all_families)
    return all_persons

def allowed_families(request):
    all_families = request.user.families_set.all()
    return all_families

def index(request):
    families = allowed_families(request)
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

    if Families.objects.get(pk=family_id) not in allowed_families(request):
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
    families = allowed_families(request)
    persons_birth = city.birth_city.all()
    persons_death = city.death_city.all()
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


class CreateModCity(LoginRequiredMixin, View):
    def get(self, request, pk):
        if pk is None:
            form = CityForm
        else:
            city = Cities.objects.get(pk=pk)
            if city.author != request.user:
                return render(request, 'not_allowed.html',
                              {'title': "Nie masz uprawnień do modyfikacji {}".format(city)})
            form = CityForm(instance=city)
        return render(request, 'add_mod_city.html', {'form':form})

    def post(self, request, pk):
        if pk is None:
            form = CityForm(request.POST)
            if form.is_valid():
                city = form.save(commit=False)
                city.author = request.user
                city.save()
                return redirect('/cities')
            else:
                return render(request, 'add_mod_city.html', {'form': form})
        else:
            city = Cities.objects.get(pk=pk)
            if city.author != request.user:
                return render(request, 'not_allowed.html',
                              {'title': "Nie masz uprawnień do modyfikacji {}".format(city)})

            form = CityForm(instance=city)

        return render (request, 'add_mod_city.html', {'form':form})

class DelCity(LoginAuthorMixin, DeleteView):
    login_url = '/login'
    template_name = 'add_mod_record.html'
    model = Cities
    success_url = '/cities'

    def get_context_data(self, **kwargs):
        context = super(DelCity, self).get_context_data(**kwargs)
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
    families = allowed_families(request)

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


class CreateModPerson(LoginRequiredMixin, View):

    def get(self, request, pk=None):

        if pk is None:
            form = PersonForm()
        else:
            person = Persons.objects.get(pk=pk)
            if person.author != request.user:
                return render(request, 'not_allowed.html',
                              {'title': "Nie masz uprawnień do modyfikacji {}".format(person)})

            form = PersonForm(instance=person, initial={
                'sex': int(person.sex),
                'deceased': int(person.deceased)
            })

            # form.fields['sex'].initial = person.sex

            print(person.sex)
            print(person.deceased)

        form.fields['family'].queryset = allowed_families(request)
        form.fields['parents'].queryset = allowed_persons(request)
        form.fields['siblings'].queryset = allowed_persons(request)
        form.fields['spouses'].queryset = allowed_persons(request)

        ctx = {
            'form': form
        }
        return render(request, 'add_mod_person.html', ctx)

    def post(self, request, pk=None):

        if pk is None:
            form = PersonForm(request.POST)

            if form.is_valid():
                object = form.save(commit=False)
                object.author = request.user
                list_families = request.POST.getlist('family')
                list_siblings = request.POST.getlist('siblings')
                list_parents = request.POST.getlist('parents')
                list_spouses = request.POST.getlist('spouses')
                object.save()
                object.family.add(*list_families)
                object.siblings.add(*list_siblings)
                object.parents.add(*list_parents)
                object.spouses.add(*list_spouses)
                object.save()
                for sibling in object.siblings.all():
                    if object not in sibling.siblings.all():
                        sibling.siblings.add(object)
                for spouse in object.spouses.all():
                    if object not in spouse.spouses.all():
                        spouse.spouses.add(object)
                return redirect('/persons')
            else:
                ctx = {'form': form}
                return render(request, 'add_mod_person.html', ctx)
        else:
            instance = Persons.objects.get(pk=pk)
            if instance.author != request.user:
                return render(request, 'not_allowed.html',
                              {'title': "Nie masz uprawnień do modyfikacji {}".format(instance)})
            form = PersonForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()

                for sibling in instance.siblings.all():
                    if instance not in sibling.siblings.all():
                        sibling.siblings.add(pk)

                for spouse in instance.spouses.all():
                    if instance not in spouse.spouses.all():
                        spouse.spouses.add(pk)

                return redirect('/persons')
            else:
                ctx = {'form': form}
                return render(request, 'add_mod_person.html', ctx)


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


def show_tree(node, level=0, d=None, parent=None):
    if d==None:
        d = {}
    if not len(d):
        d[level] = [['<ul class="tree_map">', '<li>', '<a href="/person/', node.pk, '">',
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

@login_required(login_url='/login')
def family_tree(request, pk=None):
    families = request.user.families_set.all()

    if pk == None:
        pk = families[0].pk

    family = Families.objects.get(pk=pk)

    if family.senior == None:
        ctx = {
            'list': '<p><b>Ustaw seniora rodu</b></p>',
            'families': families,
            'family': family
        }

        return render(request, 'view_base.html', ctx)

    senior = family.senior
    d = {}
    show_tree(node=senior, d=d, parent=senior)
    new_list = []
    new_list.extend(d[0][0][:-1])
    for j in range(1, len(d)):
        list_temp = []
        for i in range(len(d[j])):
            if i == 0:
                list_temp.extend(d[j][i][:-2])
                if i == (len(d[j])-1):
                    parent_node = d[j][i][-1]
                    list_temp.append('</ul>')
                    idx = new_list.index(parent_node) + 4
                    new_list[idx:idx] = list_temp
                    list_temp = []
            elif d[j][i][-1] == d[j][i-1][-1]:
                list_temp.extend(d[j][i][1:-2])
                if i == (len(d[j])-1):
                    parent_node = d[j][i][-1]
                    list_temp.append('</ul>')
                    idx = new_list.index(parent_node) + 4
                    new_list[idx:idx] = list_temp
                    list_temp = []
            else:
                parent_node = d[j][i-1][-1]
                idx = new_list.index(parent_node) + 4
                list_temp.append('</ul>')
                new_list[idx:idx] = list_temp
                list_temp = []
                list_temp.extend(d[j][i][:-2])
                if i == (len(d[j])-1):
                    parent_node = d[j][i][-1]
                    idx = new_list.index(parent_node) + 4
                    new_list[idx:idx] = list_temp
                    list_temp = []

    final = []
    for element in new_list:
        final.append(str(element))
    ctx={
        'list': ''.join(final),
        'families': families,
        'family': family
    }
    print(family.name)

    return render(request, 'view_base.html', ctx)


def render_test(request):
    return render(request, 'test.html')
