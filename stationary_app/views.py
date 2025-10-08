from django.shortcuts import render, redirect,get_object_or_404
from .form import signupform,PasswordResetConfirmForm,PasswordResetForm,UserProfileUpdateForm,UserUpdateForm,ProductForm,CategoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UserProfile,Product,Category
from django.contrib.auth.models import User


# Create your views here.
def home_page(request):
    return render(request, 'index.html')

def shop_page(request, category_name=None):
    if category_name:
        category = get_object_or_404(Category, name=category_name)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_name,
    }
    return render(request, 'shop.html', context)

def product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'admin_dashboard/product_details.html', {'product': product})

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
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})

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
    
@login_required
def profile_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile') 
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=user_profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profile.html', context)

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all()  
    context = {
        'products': products  
    }
    return render(request, 'admin_dashboard/admin_dashboard.html', context)

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
    product = Product.objects.get(pk=pk)
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
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'admin_dashboard/delete_product.html', {'product': product})

@login_required
@user_passes_test(is_admin)
def admin_categories(request):
    categories = Category.objects.all()
    context = {'categories':categories}
    return render(request,'admin_category/admin_categories.html',context)

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'admin_category/add_category.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('admin_categories')
    return render(request, 'admin_category/delete_category.html', {'category': category})