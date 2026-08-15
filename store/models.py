from django.db import models
import datetime
# Used for setting the default date on orders


class Category(models.Model):
    # Defines a database table for product categories
    name = models.CharField(max_length=50)
    # Stores the category name as text

    @staticmethod
    def get_all_categories():
        # Returns all category records from the database
        return Category.objects.filter(products__is_active=True).distinct()

    def __str__(self):
        # Controls how a category is displayed in admin and shell
        return self.name

    class Meta:
        # Changes the plural name shown in the Django admin panel
        verbose_name_plural = "Categories"


class Products(models.Model):
    # Defines a database table for products
    name = models.CharField(max_length=60)
    # Product name

    price = models.IntegerField(default=0)
    # Product price stored as a whole number

    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    # Links each product to one category
    # If the category is deleted, related products are also deleted

    description = models.CharField(max_length=250, default="", blank=True, null=True)
    # Optional text description of the product

    image = models.ImageField(upload_to="uploads/products/")
    # Stores the product image in the uploads/products/ folder

    is_active = models.BooleanField(default=True)
    # Keeps retired pieces out of the live storefront while preserving order history

    shopify_variant_id = models.CharField(max_length=120, blank=True, default="")
    # Retained only for historical records. The live checkout no longer uses Shopify.

    @staticmethod
    def get_products_by_id(ids):
        # Returns products whose IDs are in the given list
        return Products.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        # Returns all product records
        return Products.objects.filter(is_active=True).select_related("category").order_by("-category__name", "name")

    @staticmethod
    def get_all_products_by_categoryid(category_id):
        # Returns products for a specific category
        # If no category is given, return all products
        if category_id:
            return Products.objects.filter(category=category_id, is_active=True).select_related("category").order_by("name")
        return Products.get_all_products()

    def __str__(self):
        # Controls how a product is displayed
        return self.name


class Customer(models.Model):
    # Defines a database table for customers
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    # Email must be unique so two customers cannot register with the same email

    password = models.CharField(max_length=100)
    # Stores password text

    def register(self):
        # Saves the customer to the database
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        # Tries to find a customer by email
        try:
            return Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return False

    def isExists(self):
        # Checks whether this customer already exists in the database
        return Customer.objects.filter(email=self.email).exists()

    def __str__(self):
        # Displays the customer name in admin and shell
        return f"{self.first_name} {self.last_name}"

    class Meta:
        # Changes plural display name in Django admin
        verbose_name_plural = "Customers"


class Order(models.Model):
    # Defines a database table for orders
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    # Each order is connected to one product

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # Each order is connected to one customer

    quantity = models.IntegerField(default=1)
    # Number of items ordered

    price = models.IntegerField()
    # Total price for the order

    address = models.CharField(max_length=50, default="", blank=True)
    # Shipping address

    phone = models.CharField(max_length=50, default="", blank=True)
    # Contact phone number

    date = models.DateField(default=datetime.date.today)
    # Automatically sets today's date when the order is created

    status = models.BooleanField(default=False)
    # False could mean pending, True could mean completed/shipped

    def placeOrder(self):
        # Saves the order to the database
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        # Returns all orders for one customer, newest first
        return Order.objects.filter(customer=customer_id).order_by("-date")

    def __str__(self):
        # Displays the order ID in admin and shell
        return f"Order #{self.id}"

    class Meta:
        # Changes plural display name in Django admin
        verbose_name_plural = "Orders"


class ShopifyOrder(models.Model):
    # Historic order-sync records are kept intact while Stripe powers new purchases.
    shopify_order_id = models.CharField(max_length=80, unique=True)
    order_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    financial_status = models.CharField(max_length=50, blank=True)
    fulfillment_status = models.CharField(max_length=50, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, blank=True)
    line_items = models.JSONField(default=list)
    received_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Shopify orders"


class StripeOrder(models.Model):
    stripe_checkout_session_id = models.CharField(max_length=255, unique=True)
    payment_intent_id = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    payment_status = models.CharField(max_length=30, default="pending")
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="usd")
    shipping_name = models.CharField(max_length=120, blank=True)
    shipping_address = models.JSONField(default=dict)
    line_items = models.JSONField(default=list)
    received_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripe order {self.stripe_checkout_session_id}"

    class Meta:
        verbose_name_plural = "Stripe orders"
