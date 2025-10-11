from django.shortcuts import render, redirect,get_object_or_404
from .form import signupform,PasswordResetConfirmForm,PasswordResetForm,UserProfileUpdateForm,UserUpdateForm,ProductForm,CategoryForm,ProductImageForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UserProfile,Product,Category,ProductImage,Cart,CartItem
from django.contrib.auth.models import User
from django.db.models import Q # Import Q object for complex lookups
from django.core.paginator import Paginator
from decimal import Decimal
import os


# Create your views here.
def home_page(request):
    return render(request, 'index.html')

def shop_page(request, category_name=None):
    products = Product.objects.all()
    categories = Category.objects.all()
    selected_category = category_name

    # Check for a search query
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    
    # Filter by category if a category name is provided
    if category_name:
        category = get_object_or_404(Category, name=category_name)
        products = products.filter(category=category)
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        paginator = Paginator(products, 3)
        page = request.GET.get('page')  # Get the current page number from the URL query parameter 'page'
        paged_products = paginator.get_page(page)
        product_count = products.count() # Get the products for the requested page

    context = {
        'products': paged_products,
        'categories': categories,
        'selected_category': selected_category,
        'product_count' : product_count,
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
    product = get_object_or_404(Product, pk=pk)
    images = product.images.all() # Fetch all images related to the product
    
    if request.method == 'POST':
        # Create form instances with POST data and files
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        
        # Handle the deletion of existing images
        delete_image_ids = request.POST.getlist('delete_image_ids')
        for image_id in delete_image_ids:
            try:
                # Find the image object by its ID and delete it
                image_to_delete = ProductImage.objects.get(id=image_id)
                image_to_delete.delete()
            except ProductImage.DoesNotExist:
                # Handle cases where the image might not exist
                pass

        # Handle new image uploads
        if 'images' in request.FILES:
            for file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=file)

        # Save the main product form
        if product_form.is_valid():
            product_form.save()
            return redirect('admin_dashboard')
            
    else:
        # For a GET request, initialize the forms
        product_form = ProductForm(instance=product)
        
    context = {
        'form': product_form,
        'product': product,
        'images': images, # Pass the fetched images to the template
    }
    return render(request, 'admin_dashboard/edit_product.html', context)

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
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category 
    }

    return render(request, 'admin_category/edit_category.html', context)

@login_required
@user_passes_test(is_admin)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('admin_categories')
    return render(request, 'admin_category/delete_category.html', {'category': category})

login_required
@user_passes_test(is_admin)
def add_product_image(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.product = product
            image.save()
            return redirect('admin_dashboard')
    else:
        form = ProductImageForm()
    return render(request, 'admin_dashboard/add_product_image.html', {'form': form, 'product': product})

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# Add an item to the cart
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
    return redirect('cart')

# Remove an item from the cart (decrease quantity)
def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

# Remove a specific item from the cart
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

# Display the cart page
def cart_page(request):
    total = Decimal('0.00')
    tax = Decimal('0.00')
    grand_total = Decimal('0.00')
    cart_items = None
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
        tax = (2 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass
        
    context = {
        'total': total,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)