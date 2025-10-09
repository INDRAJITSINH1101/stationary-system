from django import forms
from django.contrib.auth.models import User
from .models import UserProfile,Product
import re
from django.core.exceptions import ValidationError
from .models import Category


class signupform(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput)
  confirm_password = forms.CharField(widget=forms.PasswordInput)
  email = forms.EmailField(required=True)

  class Meta:
    model = User
    fields = ['username','email','password']

  def clean_email(self):
      email = self.cleaned_data.get('email')
      pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

      if not re.match(pattern, email):
        raise ValidationError("Invalid email format. Please enter a valid email address.")

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
  
class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username not found. Please enter a correct username.")
        return username

class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mobile_number', 'address']

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number and not mobile_number.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        return mobile_number
     
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','category','company','price','description','image']



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']



    