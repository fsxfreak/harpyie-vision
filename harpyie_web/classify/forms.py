from django.contrib.auth.models import User
from django import forms

class UserForm(forms.Form):
  username = forms.CharField(label='Username', max_length=30)
  def clean_username(self):
    name = self.cleaned_data['username']
    if User.objects.filter(username=name).exists():
      raise forms.ValidationError('That user already exists')
    return name;

class LoginForm(forms.Form):
  username = forms.CharField(label='Username', max_length=30)
  def clean_username(self):
    name = self.cleaned_data['username']
    if User.objects.filter(username=name).exists():
      user = User.objects.get(username=name)
      if not user.is_superuser:
        return name;
    raise forms.ValidationError('That user does not exist')
    return False
