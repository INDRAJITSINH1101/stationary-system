from django.shortcuts import render,redirect
from .form import signupform
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
def home_page(request):
    return render(request, 'index.html')

def shop_page(request):
    return render(request, 'shop.html')

def about_page(request):
    return render(request, 'about.html')

def services_page(request):
    return render(request, 'services.html')

def contact_page(request):
    return render(request, 'contact.html')

def cart_page(request):
    return render(request, 'cart.html')

def checkout_page(request):
    return render(request, 'checkout.html')

def thankyou_page(request):
    return render(request, 'thankyou.html')

def blog_page(request):
    return render(request, 'blog.html')

def signup_view(request): 
    if request.method == 'POST':
        form = signupform(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('signin')
        
        
    else:
        form = signupform()
    return render(request, 'signup.html',{'form':form})

def signin_view(request): 
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect('home')
    
def profile_view(request): 
    return render(request, 'profile.html')

