from django.shortcuts import render, redirect
from .form import signupform,ProductForm,PasswordResetConfirmForm,PasswordResetForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Products
from django.contrib.auth.models import User

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
            login(request, user)
            return redirect('home')
        
        
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

def custom_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            request.session['password_reset_username'] = username 
            return redirect('password_reset_confirm')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

def password_reset_confirm(request):
    username = request.session.get('password_reset_username')
    if not username:
        return redirect('password_reset')  

    user = User.objects.get(username=username)

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            del request.session['password_reset_username']
            return redirect('signin')
    else:
        form = PasswordResetConfirmForm()

    return render(request, 'password_reset_confirm.html', {'form': form, 'username': username})
    
def profile_view(request): 
    return render(request, 'profile.html')

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Products.objects.all()
    context = {'products': products}
    return render(request, 'admin_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'admin_dashboard/add_product.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_product(request, pk):
    product = Products.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_dashboard/edit_product.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_product(request, pk):
    product = Products.objects.get(pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'admin_dashboard/delete_product.html', {'product': product})

