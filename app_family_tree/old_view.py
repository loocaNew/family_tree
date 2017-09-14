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
