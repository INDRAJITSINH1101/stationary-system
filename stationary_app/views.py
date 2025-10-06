from django.shortcuts import render, redirect
from .form import signupform,ProductForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Products

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

