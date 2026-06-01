from django.urls import path
# path() is used to define URL routes

from . import views
# Import the view functions/classes from this app


urlpatterns = [
    path('', views.home, name='homepage'),
    # Home page

    path('products/', views.product_list, name='products'),
    # Product listing page

    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # Product detail page
    # <int:pk> means this route expects an integer primary key

    path('cart/', views.cart, name='cart'),
    # Cart page
    # This fixes the NoReverseMatch error for {% url 'cart' %}

    path('checkout/', views.checkout, name='checkout'),
    # Checkout form that saves customer/order rows to the database

    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    # Confirmation page for the most recent database-backed checkout
]
