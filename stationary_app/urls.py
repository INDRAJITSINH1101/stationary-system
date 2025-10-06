from django.urls import path
from .import views

urlpatterns = [
    path('', views.home_page,name='home'),
    path('shop/',views.shop_page,name='shop'),
    path('about/', views.about_page,name='about'),
    path('services/',views.services_page,name='services'),
    path('contact/', views.contact_page,name='contact'),
    path('cart/', views.cart_page,name='cart'),
    path('checkout/', views.checkout_page,name='checkout'),
    path('thankyou/', views.thankyou_page,name='thankyou'),
    path('blog/', views.blog_page,name='blog'),
    path('signup/', views.signup_view, name='signup'), 
    path('signin/', views.signin_view, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'), 
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/add/', views.add_product, name='add_product'),
    path('admin_dashboard/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('admin_dashboard/delete/<int:pk>/', views.delete_product, name='delete_product'),
]

