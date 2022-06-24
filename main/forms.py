from django import forms
from .models import CmnUser, SubHeading, SuperHeading, Ad,AddImage
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .apps import regsd_user
from django.forms import inlineformset_factory
from captcha.fields import CaptchaField

from .models import Comment


class UserInfoChange(forms.ModelForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = CmnUser
        fields = ('username','first_name','last_name','email','alert_message')

class UserRegister(forms.ModelForm):
    email = forms.EmailField(required=True, label='Емейл')
    password1 = forms.CharField(label='Пароль',widget=forms.PasswordInput,help_text=password_validation._password_validators_help_text_html())
    password2 = forms.CharField(label='Повтор паролю',widget=forms.PasswordInput, help_text="Input your password again")

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError(
                'Passwords are mismatch', code='password_mismatch')}
            raise ValidationError(errors)
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        regsd_user.send(UserRegister, instance=user)
        return user

    class Meta:
        model = CmnUser
        fields = ('username','first_name', 'last_name', 'email', 'password1', 'password2', 'alert_message')

class SubHeadingForm(forms.ModelForm):
    super_heading = forms.ModelChoiceField(queryset=SuperHeading.objects.all(), empty_label=None,label='Main Heading', required=True)

    class Meta:
        model=SubHeading
        fields='__all__'

class SearchForm(forms.Form):
    keyword = forms.CharField(required=False,max_length=30,label='')

class AdForm(forms.ModelForm):
    class Meta:
        model=Ad
        fields='__all__'
        widgets = {'author': forms.HiddenInput}

AIFormSet = inlineformset_factory(Ad,AddImage,fields='__all__')

class UserCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude=('is_active',)
        widgets={'ad':forms.HiddenInput}


class GuestCommentForm(forms.ModelForm):
    captcha = CaptchaField(label='Input text from picture', error_messages={'invalid':'Wrong Text'})

    class Meta:
        model=Comment
        exclude=('is_active',)
        widgets={'ad':forms.HiddenInput}


