from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from importlib import import_module
import logging

from django.conf import settings
from django.urls import reverse


logger = logging.getLogger(__name__)


class StripeCheckoutError(Exception):
    """Raised when a cart cannot be handed to Stripe Checkout."""


class StripeWebhookError(Exception):
    """Raised when Stripe cannot verify an incoming webhook."""


def _amount_in_cents(amount):
    try:
        return int(
            (Decimal(str(amount)) * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )
    except (InvalidOperation, TypeError, ValueError) as error:
        raise StripeCheckoutError("Secure checkout is temporarily unavailable. Please try again shortly.") from error


def _stripe_client():
    if not settings.STRIPE_SECRET_KEY:
        raise StripeCheckoutError("Secure checkout is not configured yet. Please try again shortly.")

    try:
        stripe = import_module("stripe")
    except ImportError as error:
        raise StripeCheckoutError("Secure checkout is temporarily unavailable. Please try again shortly.") from error

    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def _checkout_item_summary(cart_items):
    """Keep a readable, non-sensitive item summary on the Stripe payment."""
    pieces = []
    for item in cart_items:
        size = f" ({item['size']})" if item.get("size") else ""
        pieces.append(f"{item['quantity']}x {item['product'].name}{size}")

    return "; ".join(pieces)[:450]


def create_checkout_session(request, cart_items, shipping_amount, service_fee_amount=0):
    """Create a Stripe-hosted payment session from the server-side cart."""
    if not settings.STRIPE_CHECKOUT_ENABLED:
        raise StripeCheckoutError("Secure checkout is being connected. Please try again shortly.")

    stripe = _stripe_client()
    line_items = [
        {
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": (
                        f"{item['product'].name} - {item['size']}"
                        if item.get("size")
                        else item["product"].name
                    ),
                },
                "unit_amount": _amount_in_cents(item["product"].price),
            },
            "quantity": item["quantity"],
        }
        for item in cart_items
    ]
    service_fee_cents = _amount_in_cents(service_fee_amount)
    if service_fee_cents:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Service fee"},
                    "unit_amount": service_fee_cents,
                },
                "quantity": 1,
            }
        )
    success_url = request.build_absolute_uri(reverse("stripe_success"))
    success_url = f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}"
    item_summary = _checkout_item_summary(cart_items)

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            shipping_address_collection={
                "allowed_countries": settings.STRIPE_SHIPPING_COUNTRIES,
            },
            shipping_options=[
                {
                    "shipping_rate_data": {
                        "type": "fixed_amount",
                        "display_name": "Flat-rate shipping",
                        "fixed_amount": {
                            "amount": _amount_in_cents(shipping_amount),
                            "currency": "usd",
                        },
                    },
                },
            ],
            success_url=success_url,
            cancel_url=request.build_absolute_uri(reverse("cart")),
            submit_type="pay",
            metadata={"items": item_summary},
            payment_intent_data={
                "description": f"Dune Dogs order: {item_summary}",
                "metadata": {"items": item_summary},
            },
        )
    except stripe.error.StripeError as error:
        logger.error(
            "Stripe Checkout session creation failed: type=%s code=%s param=%s request_id=%s",
            getattr(error, "type", None),
            getattr(error, "code", None),
            getattr(error, "param", None),
            getattr(error, "request_id", None),
        )
        if isinstance(error, stripe.error.AuthenticationError):
            logger.warning("Stripe Checkout rejected the configured secret key.")
            if settings.DEBUG:
                raise StripeCheckoutError(
                    "Stripe rejected the test secret key. Replace it with a current test-mode secret key and restart the preview."
                ) from error
        raise StripeCheckoutError("Secure checkout is temporarily unavailable. Please try again shortly.") from error

    if not session.url or not session.id:
        raise StripeCheckoutError("Secure checkout is temporarily unavailable. Please try again shortly.")

    return session


def construct_webhook_event(payload, signature):
    """Verify Stripe's raw webhook payload before using its contents."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise StripeWebhookError("Missing Stripe webhook secret.")

    try:
        stripe = _stripe_client()
    except StripeCheckoutError as error:
        raise StripeWebhookError("Secure checkout is temporarily unavailable.") from error

    try:
        return stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError) as error:
        raise StripeWebhookError("Invalid Stripe webhook signature.") from error
