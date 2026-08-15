from django.urls import path
# path() is used to define URL routes

from . import views
# Import the view functions/classes from this app


urlpatterns = [
    path('healthz/', views.healthcheck, name='healthcheck'),
    # Deployment health check

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
    # Secure handoff to Stripe Checkout

    path('checkout/success/', views.stripe_success, name='stripe_success'),
    # Return page after Stripe Checkout

    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    # Verified payment status updates from Stripe
]
