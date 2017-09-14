from django.contrib.auth.models import User
from app_family_tree.views import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.widgets import AdminDateWidget


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class UpdateProfile(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class DateTypeInput(forms.DateInput):
    input_type = 'date'


class PersonForm(forms.ModelForm):
    class Meta:
        model = Persons
        fields = ['name',
                  'surname',
                  'description',
                  'deceased',
                  'sex',
                  'birth_date',
                  'birth_city',
                  'death_date',
                  'death_city',
                  'parents',
                  'siblings',
                  'spouses',
                  'family']

        widgets = {
            'sex': forms.RadioSelect,
            'deceased': forms.RadioSelect,
            'birth_date': DateTypeInput,
            'death_date': DateTypeInput,
        }

    def __init__(self, *args, **kwargs):
        # user = kwargs.pop('user')
        super(PersonForm, self).__init__(*args, **kwargs)
        for field, value in self.fields.items():
            value.widget.attrs['class'] = 'form-control'
        # self.fields['family'].queryset = Families.objects.filter(user=user)


class CityForm(forms.ModelForm):
    class Meta:
        model = Cities
        fields = ['name',
                  'description']


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Families
        fields = ['name',
                  'description']