from django.urls import path
from . import views

from django.conf.urls import include, url
from qr_code import urls as qr_code_urls

urlpatterns = [
    # associate views to url routing here
    path('', views.login_action, name='home'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register_vendor', views.vendor_register_action, name='register_vendor'),
    path('register_customer', views.customer_register_action, name='register_customer'),
    path('home_vendor', views.home_vendor, name='home_vendor'),
    path('home_customer', views.home_customer, name='home_customer'),
    path('add_meal', views.add_meal, name='add_meal'),
    path('delete_meal/<int:id>', views.delete_meal, name='delete_meal'),
    path('menu_detail/<int:vendor_id>', views.menu_detail,
         name='menu_detail'),
    path('mealPic/<int:id>', views.mealPic, name='mealPic'),
    path('profilePic/<int:id>', views.profilePic, name='profilePic'),
    path('add_to_cart/<int:vendor_id>/<int:meal_id>', views.add_to_cart,
         name='add_to_cart'),
    path('shopping_cart', views.shopping_cart, name='shopping_cart'),
    path('charge', views.charge, name='charge'),
    path('orders_history', views.orders_history, name='orders_history'),
    path('customer_profile', views.customer_profile, name='customer_profile'),
    path('pickup_confirmation/<int:order>', views.pickup_confirmation, name='pickup_confirmation'),
    path('vendor_profile', views.vendor_profile, name='vendor_profile'),
    path('order_success', views.order_success, name='order_success'),
    path('qrcode_page/<int:order>/<slug:token>', views.qrcode_page, name='qrcode_page'),
    path('error_page', views.error_page, name='error_page'),
    url(r'^qr_code/', include(qr_code_urls, namespace="qr_code")),
]
