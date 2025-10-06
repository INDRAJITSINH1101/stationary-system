from django import forms
from django.contrib.auth.models import User
from .models import Products


class signupform(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput)
  confirm_password = forms.CharField(widget=forms.PasswordInput)
  email = forms.EmailField(required=True)

  class Meta:
    model = User
    fields = ['username','email','password']

  def clean_email(self):
      email = self.cleaned_data.get('email')
      if not email or '@' not in email:
          raise forms.ValidationError("Please enter a valid email address.")
      return email

  def clean(self):
      cleaned_data = super().clean()
      password = cleaned_data.get('password')
      confirm_password = cleaned_data.get('confirm_password')

      if password and len(password) < 8:
          self.add_error('password', "Password must be at least 8 characters long.")

      if password and confirm_password and password != confirm_password:
          self.add_error('confirm_password', "Passwords do not match.")

      return cleaned_data
  
  def save(self, commit=True):
      user = super().save(commit=False)
      user.set_password(self.cleaned_data["password"])
      user.email = self.cleaned_data["email"]
      if commit:
          user.save()
      return user
     
     
class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'description', 'price', 'image']

    