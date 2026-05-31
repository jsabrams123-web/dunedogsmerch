from django.shortcuts import render, get_object_or_404, redirect
# render: returns an HTML page with data
# get_object_or_404: returns an object or a 404 page if it does not exist
# redirect: sends the user to another URL after a POST request

from .models import Category, Products, Customer, Order
# Import the database models used by this app


def _get_cart(request):
    """
    Helper function to get the cart from the session.
    If no cart exists yet, return an empty dictionary.
    """
    return request.session.get("cart", {})


def _save_cart(request, cart):
    """
    Helper function to save the updated cart back into the session.
    """
    request.session["cart"] = cart
    request.session.modified = True


def _build_store_context(request):
    """
    Build the common context used by the store pages.
    This includes:
    - products
    - categories
    - cart
    - cart_count
    """
    categories = Category.get_all_categories()
    # Get all categories from the database

    category_id = request.GET.get("category")
    # Read category filter from the query string, for example ?category=1

    if category_id:
        products = Products.get_all_products_by_categoryid(category_id)
        # Show only products from the selected category
    else:
        products = Products.get_all_products()
        # Show all products if no category is selected

    cart = _get_cart(request)
    # Get the current session cart

    cart_count = sum(cart.values())
    # Count total number of items in the cart

    return {
        "products": products,
        "categories": categories,
        "cart": cart,
        "cart_count": cart_count,
    }


def _update_cart(request):
    """
    Handle add/remove actions coming from POST forms.

    Expected POST fields:
    - product: product id
    - remove: optional field; if present, remove one item instead of adding one
    """
    product_id = request.POST.get("product")
    remove = request.POST.get("remove")

    if not product_id:
        return

    cart = _get_cart(request)

    pid = str(product_id)
    quantity = cart.get(pid, 0)

    if remove:
        # Remove one item, or remove the item entirely if the quantity becomes zero
        if quantity <= 1:
            cart.pop(pid, None)
        else:
            cart[pid] = quantity - 1
    else:
        # Add one item
        cart[pid] = quantity + 1

    _save_cart(request, cart)


def home(request):
    """
    Homepage view.

    GET:
    - Shows products and categories
    - Supports category filtering

    POST:
    - Adds/removes items from the cart
    """
    if request.method == "POST":
        _update_cart(request)
        return redirect("homepage")

    context = _build_store_context(request)
    return render(request, "store/index.html", context)


def product_list(request):
    """
    Product listing page.

    GET:
    - Shows products and categories
    - Supports category filtering

    POST:
    - Adds/removes items from the cart
    """
    if request.method == "POST":
        _update_cart(request)
        return redirect("products")

    context = _build_store_context(request)
    return render(request, "store/products.html", context)


def product_detail(request, pk):
    """
    Product detail page.

    GET:
    - Shows one product

    POST:
    - Adds/removes items from the cart
    """
    product = get_object_or_404(Products, pk=pk)

    if request.method == "POST":
        _update_cart(request)
        return redirect("product_detail", pk=pk)

    cart = _get_cart(request)

    return render(request, "store/product_detail.html", {
        "product": product,
        "cart": cart,
        "cart_count": sum(cart.values()),
    })


def customer_orders(request):
    """
    Orders page.
    Displays all orders in the database.
    """
    orders = Order.objects.all()

    cart = _get_cart(request)

    return render(request, "store/orders.html", {
        "orders": orders,
        "cart": cart,
        "cart_count": sum(cart.values()),
    })


def cart(request):
    """
    Cart page.

    GET:
    - Displays all items currently stored in the session cart

    POST:
    - Lets the user add/remove items directly from the cart page
    """
    if request.method == "POST":
        _update_cart(request)
        return redirect("cart")

    cart = _get_cart(request)
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Products.objects.get(id=product_id)
            item_total = product.price * quantity
            total += item_total

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total,
            })
        except Products.DoesNotExist:
            # If a product was deleted from the database, skip it
            continue

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total": total,
        "cart_count": sum(cart.values()),
    })