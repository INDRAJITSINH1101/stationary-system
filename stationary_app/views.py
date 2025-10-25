from django.shortcuts import render, redirect,get_object_or_404
from .form import signupform,PasswordResetConfirmForm,PasswordResetForm,UserProfileUpdateForm,UserUpdateForm,ProductForm,CategoryForm,ProductImageForm,SubCategoryForm,SubSubCategoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UserProfile,Product,Category,ProductImage,Cart,CartItem,Order,OrderItem,SubCategory,SubSubCategory
from django.contrib.auth.models import User
from django.db.models import Q # Import Q object for complex lookups
from django.core.paginator import Paginator
from decimal import Decimal
import os

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest,HttpResponse,JsonResponse
from weasyprint import HTML, CSS







# Create your views here.
def home_page(request):
    categories = Category.objects.all().prefetch_related('subcategories__subsubcategories')
    
    context = {
        'categories': categories,
    }
    return render(request, 'index.html',context)



def shop_page(request, subsubcategory_pk=None): 
    products = Product.objects.all().select_related('subsubcategory__subcategory__category')
    categories = Category.objects.all().prefetch_related('subcategories__subsubcategories')
    selected_subsubcategory = None 

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    
    if subsubcategory_pk:
        subsubcategory = get_object_or_404(SubSubCategory, pk=subsubcategory_pk) 
        products = products.filter(subsubcategory=subsubcategory)
        selected_subsubcategory = subsubcategory.name 
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        paginator = Paginator(products, 3)
        page = request.GET.get('page')  
        paged_products = paginator.get_page(page)
        product_count = products.count()

    subcategories = SubCategory.objects.all() 
    
    context = {
        'products': paged_products,
        'categories': categories, 
        'subcategories': subcategories, 
        'selected_subsubcategory': selected_subsubcategory, 
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

def thankyou_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'thankyou.html', context)

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
    products = Product.objects.all().select_related('subsubcategory__subcategory__category') 
    context = {
        'products': products  
    }
    return render(request, 'admin_dashboard/admin_dashboard.html', context)

def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).order_by('name')
    subcategory_list = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
    return JsonResponse(subcategory_list, safe=False)

def load_subsubcategories(request):
    subcategory_id = request.GET.get('subcategory_id')
    subsubcategories = SubSubCategory.objects.filter(subcategory_id=subcategory_id).order_by('name')
    subsub_list = [{'id': subsub.id, 'name': subsub.name} for subsub in subsubcategories]
    return JsonResponse(subsub_list, safe=False)


@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.subcategory = form.cleaned_data['subcategory']
            product.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'admin_dashboard/add_product.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    images = product.images.all()
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        
      
        delete_image_ids = request.POST.getlist('delete_image_ids')
        for image_id in delete_image_ids:
            try:
                image_to_delete = ProductImage.objects.get(id=image_id)
                image_to_delete.delete()
            except ProductImage.DoesNotExist:
                pass

        if 'images' in request.FILES:
            for file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=file)

      
        if product_form.is_valid():
            product_form.save()
            return redirect('admin_dashboard')
            
    else:
        product_form = ProductForm(instance=product)
        
    context = {
        'form': product_form,
        'product': product,
        'images': images, 
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

@login_required
@user_passes_test(is_admin)
def admin_subsubcategories(request):
    subsubcategories = SubSubCategory.objects.select_related('subcategory__category').all()
    context = {'subsubcategories': subsubcategories}
    return render(request,'admin_category/admin_subsubcategories.html',context) 

@login_required
@user_passes_test(is_admin)
def add_subsubcategory(request):
    if request.method == 'POST':
        form = SubSubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_subsubcategories') 
    else:
        form = SubSubCategoryForm()
    return render(request, 'admin_category/add_subsubcategory.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_subsubcategory(request, pk):
    subsubcategory = get_object_or_404(SubSubCategory, pk=pk)

    if request.method == 'POST':
        form = SubSubCategoryForm(request.POST, instance=subsubcategory)
        if form.is_valid():
            form.save()
            return redirect('admin_subsubcategories') 
    else:
        form = SubSubCategoryForm(instance=subsubcategory)

    context = {
        'form': form,
        'subsubcategory': subsubcategory 
    }
    return render(request, 'admin_category/edit_subsubcategory.html', context)

@login_required
@user_passes_test(is_admin)
def delete_subsubcategory(request, pk):
    subsubcategory = get_object_or_404(SubSubCategory, pk=pk)
    if request.method == 'POST':
        subsubcategory.delete()
        return redirect('admin_subsubcategories') 
    return render(request, 'admin_category/delete_subsubcategory.html', {'subsubcategory': subsubcategory})


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

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    if not product.is_in_stock:
        return redirect('shop')
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if product.stock <= cart_item.quantity: # Prevent adding more than stock available
             return redirect('cart')
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        if product.stock < 1: # Should not happen if the first check passes, but for safety
             return redirect('shop')
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
    return redirect('cart')

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

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart_page(request):
    total = Decimal('0.00')
    cgst_total = Decimal('0.00')
    sgst_total = Decimal('0.00')
    gst_total = Decimal('0.00')
    grand_total = Decimal('0.00')
    cart_items = None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            product_price = cart_item.product.price * cart_item.quantity
            total += product_price

            # Calculate GST per product
            gst_rate = cart_item.product.gst_rate
            cgst = (product_price * (gst_rate / 2)) / 100
            sgst = (product_price * (gst_rate / 2)) / 100
            total_gst = cgst + sgst

            cgst_total += cgst
            sgst_total += sgst
            gst_total += total_gst

        grand_total = total + gst_total

    except Cart.DoesNotExist:
        cart_items = []

    context = {
        'cart_items': cart_items,
        'total': round(total, 2),
        'cgst_total': round(cgst_total, 2),
        'sgst_total': round(sgst_total, 2),
        'gst_total': round(gst_total, 2),
        'grand_total': round(grand_total, 2),
    }
    return render(request, 'cart.html', context)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def checkout_page(request):
    total = Decimal('0.00')
    cgst_total = Decimal('0.00')
    sgst_total = Decimal('0.00')
    gst_total = Decimal('0.00')
    grand_total = Decimal('0.00')
    cart_items = None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            product_price = item.product.price * item.quantity
            total += product_price

            gst_rate = item.product.gst_rate
            cgst = (product_price * (gst_rate / 2)) / 100
            sgst = (product_price * (gst_rate / 2)) / 100
            total_gst = cgst + sgst

            cgst_total += cgst
            sgst_total += sgst
            gst_total += total_gst

        grand_total = total + gst_total

    except Cart.DoesNotExist:
        cart_items = []

    currency = 'INR'
    amount = int(grand_total * 100)  

    razorpay_order = razorpay_client.order.create(dict(
        amount=amount, 
        currency=currency,
        payment_capture='1' 
    ))

    context = {
        'cart_items': cart_items,
        'total': round(total, 2),
        'cgst_total': round(cgst_total, 2),
        'sgst_total': round(sgst_total, 2),
        'gst_total': round(gst_total, 2),
        'grand_total': round(grand_total, 2),
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
    }

    return render(request, 'checkout.html', context)

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            
            if result is not None:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)

                grand_total = Decimal('0.00')
                for item in cart_items:
                    product_price = item.product.price * item.quantity
                    total_gst = (product_price * item.product.gst_rate) / 100
                    grand_total += product_price + total_gst

                order = Order.objects.create(
                    user=request.user,
                    full_name=request.user.username,
                    address=request.user.userprofile.address, 
                    city="City",
                    postal_code="12345", 
                    email=request.user.email,
                    phone_number=request.user.userprofile.mobile_number,
                    total_amount=grand_total,
                    payment_method='Online',
                    payment_id=payment_id,
                    is_paid=True,
                )

                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price,
                    )
                
                cart_items.delete()
                
                return redirect('thankyou', order_id=order.id)
            else:
                return HttpResponseBadRequest("Payment verification failed")
        except Exception as e:
            return HttpResponseBadRequest(f"Error: {e}")
    else:
        return HttpResponseBadRequest()

    
def place_cod_order(request):
    if request.method == 'POST':
        user = request.user
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        if not cart_items.exists():
            return redirect('shop')

        full_name = f"{request.POST.get('c_fname')} {request.POST.get('c_lname')}"
        address = request.POST.get('c_address')
        city = request.POST.get('c_state_country') 
        postal_code = request.POST.get('c_postal_zip')
        email = request.POST.get('c_email_address')
        phone_number = request.POST.get('c_phone')

        grand_total = Decimal('0.00')
        for item in cart_items:
            product_price = item.product.price * item.quantity
            total_gst = (product_price * item.product.gst_rate) / 100
            grand_total += product_price + total_gst

        order = Order.objects.create(
            user=user,
            full_name=full_name,
            address=address,
            city=city,
            postal_code=postal_code,
            email=email,
            phone_number=phone_number,
            total_amount=grand_total,
            payment_method='COD',
            is_paid=True,
        )

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
        cart_items.delete()

        return redirect('thankyou', order_id=order.id)
    return redirect('checkout')

@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'admin_dashboard/admin_orders.html', context)

@login_required
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'admin_dashboard/admin_order_detail.html', context)

@login_required
def customer_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'invoice.html', context)

@login_required
def download_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.user != order.user and not is_admin(request.user):
        return HttpResponse("Unauthorized to view this invoice.", status=403) 
    
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
    }

    html_content = render(request, 'invoice.html', context).content.decode('utf-8')

    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_subcategories(request):
    subcategories = SubCategory.objects.select_related('category').all()
    context = {'subcategories': subcategories}
    return render(request,'admin_category/admin_subcategories.html',context) 

@login_required
@user_passes_test(is_admin)
def add_subcategory(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_subcategories') 
    else:
        form = SubCategoryForm()
    return render(request, 'admin_category/add_subcategory.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)

    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            return redirect('admin_subcategories') 
    else:
        form = SubCategoryForm(instance=subcategory)

    context = {
        'form': form,
        'subcategory': subcategory 
    }
    return render(request, 'admin_category/edit_subcategory.html', context)

@login_required
@user_passes_test(is_admin)
def delete_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        return redirect('admin_subcategories') 
    return render(request, 'admin_category/delete_subcategory.html', {'subcategory': subcategory})