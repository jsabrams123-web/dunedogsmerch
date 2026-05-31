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
        return Category.objects.all()

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

    @staticmethod
    def get_products_by_id(ids):
        # Returns products whose IDs are in the given list
        return Products.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        # Returns all product records
        return Products.objects.all()

    @staticmethod
    def get_all_products_by_categoryid(category_id):
        # Returns products for a specific category
        # If no category is given, return all products
        if category_id:
            return Products.objects.filter(category=category_id)
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