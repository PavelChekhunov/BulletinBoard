from django import forms
from .models import Post, Category
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from allauth.account.forms import LoginForm, SignupForm, PasswordField
from django.utils.translation import gettext_lazy as _

class AdvertForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:400px;font-weight:bold;'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='(Выберите категорию)',
                                      widget=forms.Select(attrs={
                                          'style': 'width:250px; height:29px;padding-bottom:2px;font-weight:bold;'
                                      }))
    text = forms.CharField(widget=CKEditorUploadingWidget(attrs={'style': 'width:715px;'}))

    class Meta:
        model = Post
        fields = ['title', 'category', 'text']


class CustomLoginForm(LoginForm):
    password = PasswordField(label=_("Пароль"), autocomplete="current-password",
                             widget=forms.PasswordInput(attrs={'style': 'width:400px;'}))

    def login(self, *args, **kwargs):
        return super(CustomLoginForm, self).login(*args, **kwargs)


class CustomSignupForm(SignupForm):

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(CustomSignupForm, self).save(request)

        # Add your own processing here.

        # You must return the original result.
        return user
