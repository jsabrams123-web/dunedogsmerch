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

    path('orders/', views.customer_orders, name='orders'),
    # Orders page

    path('cart/', views.cart, name='cart'),
    # Cart page
    # This fixes the NoReverseMatch error for {% url 'cart' %}
]