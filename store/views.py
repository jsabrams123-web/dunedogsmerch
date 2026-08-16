from decimal import Decimal, InvalidOperation, ROUND_CEILING

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Category, Products, StripeOrder
from .stripe_checkout import (
    StripeCheckoutError,
    StripeWebhookError,
    construct_webhook_event,
    create_checkout_session,
)


SHIPPING_FEE = 7


def healthcheck(request):
    """Small unauthenticated endpoint used by the hosting provider."""
    return HttpResponse("ok", content_type="text/plain")


def _get_cart(request):
    return request.session.get("cart", {})


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def _parse_cart_item_key(raw_key):
    product_key, separator, size = str(raw_key).partition(":")
    try:
        product_id = int(product_key)
    except (TypeError, ValueError):
        return None, ""

    return product_id, size.strip().upper() if separator else ""


def _cart_item_key(product, size=""):
    return f"{product.id}:{size}" if product.requires_size else str(product.id)


def _valid_cart_entries(cart):
    product_ids = {
        product_id
        for product_id, _ in (_parse_cart_item_key(key) for key in cart)
        if product_id is not None
    }
    if not product_ids:
        return []

    products = {
        product.id: product
        for product in Products.objects.filter(id__in=product_ids, is_active=True).select_related("category")
    }
    entries = []
    for raw_key, raw_quantity in cart.items():
        product_id, size = _parse_cart_item_key(raw_key)
        product = products.get(product_id)
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            continue

        if not product or quantity < 1:
            continue
        if product.requires_size and size not in product.available_sizes:
            continue
        if not product.requires_size and size:
            continue

        entries.append((str(raw_key), product, size, quantity))

    return entries


def _cart_count(cart):
    """Count only valid, still-live pieces in the storefront."""
    return sum(quantity for _, _, _, quantity in _valid_cart_entries(cart))


def _build_store_context(request):
    categories = Category.get_all_categories()
    category_id = request.GET.get("category")
    products = (
        Products.get_all_products_by_categoryid(category_id)
        if category_id
        else Products.get_all_products()
    )
    cart = _get_cart(request)

    return {
        "products": products,
        "categories": categories,
        "cart": cart,
        "cart_count": _cart_count(cart),
    }


def _update_cart(request):
    cart_item = request.POST.get("cart_item", "").strip()
    product_id = request.POST.get("product")
    remove = request.POST.get("remove")

    if cart_item:
        parsed_product_id, size = _parse_cart_item_key(cart_item)
        product = Products.objects.filter(id=parsed_product_id, is_active=True).select_related("category").first()
    else:
        product = Products.objects.filter(id=product_id, is_active=True).select_related("category").first()
        size = request.POST.get("size", "").strip().upper()

    if not product:
        return

    if product.requires_size:
        if size not in product.available_sizes:
            messages.error(request, "Choose a tee size before adding it to your cart.")
            return
    elif size:
        return

    cart_item = _cart_item_key(product, size)
    cart = _get_cart(request)
    try:
        quantity = int(cart.get(cart_item, 0))
    except (TypeError, ValueError):
        quantity = 0

    if remove:
        if quantity <= 1:
            cart.pop(cart_item, None)
        else:
            cart[cart_item] = quantity - 1
    else:
        cart[cart_item] = quantity + 1

    _save_cart(request, cart)


def home(request):
    if request.method == "POST":
        _update_cart(request)
        return redirect("homepage")

    return render(request, "store/index.html", _build_store_context(request))


def product_list(request):
    if request.method == "POST":
        _update_cart(request)
        return redirect("products")

    return render(request, "store/products.html", _build_store_context(request))


def product_detail(request, pk):
    product = get_object_or_404(Products.objects.filter(is_active=True).select_related("category"), pk=pk)

    if request.method == "POST":
        _update_cart(request)
        return redirect("product_detail", pk=pk)

    cart = _get_cart(request)
    return render(request, "store/product_detail.html", {
        "product": product,
        "cart": cart,
        "cart_count": _cart_count(cart),
    })


def _build_cart_items(cart):
    cart_items = []
    total = 0

    for cart_item, product, size, quantity in _valid_cart_entries(cart):
        item_total = product.price * quantity
        total += item_total
        cart_items.append({
            "cart_item": cart_item,
            "product": product,
            "size": size,
            "quantity": quantity,
            "item_total": item_total,
        })

    return cart_items, total


def _build_order_totals(cart):
    cart_items, subtotal = _build_cart_items(cart)
    shipping = SHIPPING_FEE if cart_items else 0
    service_fee = _stripe_service_fee(subtotal, shipping)
    return cart_items, subtotal, shipping, service_fee, subtotal + shipping + service_fee


def _money_from_cents(amount):
    try:
        return (Decimal(str(amount)) / Decimal("100")).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _money_to_cents(amount):
    try:
        return int(
            (Decimal(str(amount)) * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_CEILING,
            )
        )
    except (InvalidOperation, TypeError, ValueError):
        return 0


def _stripe_service_fee(subtotal, shipping):
    """Gross up the order so a standard card fee is paid by the customer."""
    base_cents = _money_to_cents(Decimal(str(subtotal)) + Decimal(str(shipping)))
    fixed_cents = max(settings.STRIPE_SERVICE_FEE_FIXED_CENTS, 0)
    percent = max(Decimal(str(settings.STRIPE_SERVICE_FEE_PERCENT)), Decimal("0"))
    rate = percent / Decimal("100")

    if base_cents <= 0 or (rate == 0 and fixed_cents == 0) or rate >= 1:
        return Decimal("0.00")

    gross_cents = (
        Decimal(base_cents + fixed_cents) / (Decimal("1") - rate)
    ).quantize(Decimal("1"), rounding=ROUND_CEILING)
    return _money_from_cents(max(int(gross_cents) - base_cents, 0))


def _plain_address(address):
    if not address:
        return {}

    try:
        return {
            str(key): "" if value is None else str(value)
            for key, value in dict(address).items()
        }
    except (TypeError, ValueError):
        return {}


def cart(request):
    if request.method == "POST":
        _update_cart(request)
        return redirect("cart")

    cart_data = _get_cart(request)
    cart_items, subtotal, shipping, service_fee, total = _build_order_totals(cart_data)
    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "service_fee": service_fee,
        "total": total,
        "cart_count": _cart_count(cart_data),
    })


def checkout(request):
    cart_data = _get_cart(request)
    cart_items, subtotal, shipping, service_fee, total = _build_order_totals(cart_data)

    if not cart_items:
        messages.warning(request, "Add an item before checking out.")
        return redirect("products")

    if request.method != "POST":
        return redirect("cart")

    try:
        checkout_session = create_checkout_session(request, cart_items, shipping, service_fee)
    except StripeCheckoutError as error:
        messages.error(request, str(error))
        return redirect("cart")

    StripeOrder.objects.update_or_create(
        stripe_checkout_session_id=checkout_session.id,
        defaults={
            "payment_status": "pending",
            "subtotal_amount": subtotal,
            "shipping_amount": shipping,
            "service_fee_amount": service_fee,
            "total_amount": total,
            "currency": "usd",
            "line_items": [
                {
                    "product_id": item["product"].id,
                    "name": item["product"].name,
                    "size": item["size"],
                    "quantity": item["quantity"],
                    "unit_price": item["product"].price,
                    "line_total": item["item_total"],
                }
                for item in cart_items
            ],
        },
    )
    return redirect(checkout_session.url)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    signature = request.headers.get("Stripe-Signature", "")
    try:
        event = construct_webhook_event(request.body, signature)
    except (StripeCheckoutError, StripeWebhookError):
        return HttpResponse(status=400)

    event_type = event.get("type")
    handled_events = {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
        "checkout.session.async_payment_failed",
    }
    if event_type not in handled_events:
        return HttpResponse(status=200)

    session = event.get("data", {}).get("object", {})
    session_id = str(session.get("id") or "")
    if not session_id:
        return HttpResponse(status=400)

    customer_details = session.get("customer_details") or {}
    shipping_details = session.get("shipping_details") or {}
    if not shipping_details:
        shipping_details = (session.get("collected_information") or {}).get("shipping_details") or {}
    total_details = session.get("total_details") or {}
    payment_status = session.get("payment_status") or "pending"
    if event_type == "checkout.session.async_payment_failed":
        payment_status = "failed"

    defaults = {
        "payment_intent_id": str(session.get("payment_intent") or ""),
        "email": customer_details.get("email") or "",
        "payment_status": payment_status,
        "subtotal_amount": _money_from_cents(session.get("amount_subtotal")),
        "shipping_amount": _money_from_cents(total_details.get("amount_shipping")),
        "total_amount": _money_from_cents(session.get("amount_total")),
        "currency": str(session.get("currency") or "usd"),
        "shipping_name": shipping_details.get("name") or "",
        "shipping_address": _plain_address(shipping_details.get("address")),
    }
    order, created = StripeOrder.objects.get_or_create(
        stripe_checkout_session_id=session_id,
        defaults={**defaults, "line_items": []},
    )
    if not created:
        for field, value in defaults.items():
            setattr(order, field, value)
        order.save()

    return HttpResponse(status=200)


def stripe_success(request):
    session_id = request.GET.get("session_id", "").strip()
    order = None
    if session_id:
        order = StripeOrder.objects.filter(stripe_checkout_session_id=session_id).first()
        if order:
            _save_cart(request, {})

    cart_data = _get_cart(request)
    return render(request, "store/stripe_success.html", {
        "order": order,
        "cart_count": _cart_count(cart_data),
    })
