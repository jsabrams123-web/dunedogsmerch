from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Products, StripeOrder
from .stripe_checkout import create_checkout_session
from .views import _build_order_totals


class StripeCheckoutTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="T-Shirts")
        self.product = Products.objects.create(
            name="Dune Dogs Black Logo Tee",
            price=40,
            category=category,
            description="Black Dune Dogs logo tee.",
            image="uploads/products/black_logo_tee.png",
        )

    def test_healthcheck_returns_ok(self):
        response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")

    @override_settings(
        ALLOWED_HOSTS=["dunedogshop.com"],
        SECURE_SSL_REDIRECT=True,
    )
    def test_healthcheck_allows_railways_private_probe_host(self):
        response = self.client.get("/healthz/", HTTP_HOST="100.64.0.2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")

    def test_catalog_images_use_static_asset_urls(self):
        response = self.client.get(reverse("products"))

        self.assertContains(response, "/static/uploads/products/black_logo_tee.png")
        self.assertNotContains(response, "/media/uploads/products/black_logo_tee.png")

    def _add_product_to_cart(self):
        session = self.client.session
        session["cart"] = {str(self.product.id): 2}
        session.save()

    @override_settings(
        STRIPE_CHECKOUT_ENABLED=True,
        STRIPE_SECRET_KEY="sk_test_example",
        STRIPE_SHIPPING_COUNTRIES=["US"],
    )
    @patch("store.stripe_checkout._stripe_client")
    def test_checkout_session_uses_one_flat_shipping_rate(self, stripe_client):
        stripe_client.return_value = MagicMock()
        stripe_client.return_value.checkout.Session.create.return_value = SimpleNamespace(
            id="cs_test_dune",
            url="https://checkout.stripe.com/c/test",
        )
        request = self.client.get(reverse("cart")).wsgi_request

        checkout_session = create_checkout_session(
            request,
            [{"product": self.product, "quantity": 2, "item_total": 80}],
            shipping_amount=7,
            service_fee_amount=Decimal("1.72"),
        )

        self.assertEqual(checkout_session.id, "cs_test_dune")
        options = stripe_client.return_value.checkout.Session.create.call_args.kwargs
        self.assertEqual(options["line_items"][0]["price_data"]["unit_amount"], 4000)
        self.assertEqual(options["line_items"][0]["quantity"], 2)
        self.assertEqual(options["line_items"][1]["price_data"]["product_data"]["name"], "Service fee")
        self.assertEqual(options["line_items"][1]["price_data"]["unit_amount"], 172)
        self.assertEqual(
            options["shipping_options"][0]["shipping_rate_data"]["fixed_amount"]["amount"],
            700,
        )
        self.assertIn("session_id={CHECKOUT_SESSION_ID}", options["success_url"])

    @override_settings(
        STRIPE_SERVICE_FEE_PERCENT=Decimal("2.9"),
        STRIPE_SERVICE_FEE_FIXED_CENTS=30,
    )
    @patch(
        "store.views.create_checkout_session",
        return_value=SimpleNamespace(
            id="cs_test_dune",
            url="https://checkout.stripe.com/c/test",
        ),
    )
    def test_checkout_creates_pending_stripe_order(self, create_checkout):
        self._add_product_to_cart()

        response = self.client.post(reverse("checkout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://checkout.stripe.com/c/test")
        self.assertEqual(create_checkout.call_args.args[1][0]["quantity"], 2)
        self.assertEqual(create_checkout.call_args.args[2], 7)
        self.assertEqual(create_checkout.call_args.args[3], Decimal("2.91"))

        order = StripeOrder.objects.get(stripe_checkout_session_id="cs_test_dune")
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(order.subtotal_amount, 80)
        self.assertEqual(order.shipping_amount, 7)
        self.assertEqual(order.service_fee_amount, Decimal("2.91"))
        self.assertEqual(order.total_amount, Decimal("89.91"))
        self.assertEqual(order.line_items[0]["quantity"], 2)

    @override_settings(
        STRIPE_SERVICE_FEE_PERCENT=Decimal("2.9"),
        STRIPE_SERVICE_FEE_FIXED_CENTS=30,
    )
    def test_order_total_includes_grossed_up_service_fee(self):
        cart_items, subtotal, shipping, service_fee, total = _build_order_totals(
            {str(self.product.id): 1}
        )

        self.assertEqual(len(cart_items), 1)
        self.assertEqual(subtotal, 40)
        self.assertEqual(shipping, 7)
        self.assertEqual(service_fee, Decimal("1.72"))
        self.assertEqual(total, Decimal("48.72"))

    @override_settings(STRIPE_CHECKOUT_ENABLED=False)
    def test_checkout_stays_in_cart_until_stripe_is_configured(self):
        self._add_product_to_cart()

        response = self.client.post(reverse("checkout"))

        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(StripeOrder.objects.count(), 0)

    @patch("store.views.construct_webhook_event")
    def test_verified_webhook_marks_order_paid(self, construct_event):
        StripeOrder.objects.create(
            stripe_checkout_session_id="cs_test_paid",
            payment_status="pending",
            subtotal_amount=40,
            shipping_amount=7,
            total_amount=47,
            line_items=[{"name": self.product.name, "quantity": 1, "unit_price": 40}],
        )
        construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_paid",
                    "payment_intent": "pi_test_paid",
                    "payment_status": "paid",
                    "amount_subtotal": 4000,
                    "amount_total": 4700,
                    "currency": "usd",
                    "customer_details": {"email": "fan@example.com"},
                    "shipping_details": {
                        "name": "Dune Fan",
                        "address": {
                            "line1": "1 Main Street",
                            "city": "Los Angeles",
                            "state": "CA",
                            "postal_code": "90001",
                            "country": "US",
                        },
                    },
                    "total_details": {"amount_shipping": 700},
                }
            },
        }

        response = self.client.post(
            reverse("stripe_webhook"),
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test-signature",
        )

        self.assertEqual(response.status_code, 200)
        order = StripeOrder.objects.get(stripe_checkout_session_id="cs_test_paid")
        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(order.payment_intent_id, "pi_test_paid")
        self.assertEqual(order.email, "fan@example.com")
        self.assertEqual(order.total_amount, 47)
        self.assertEqual(order.shipping_address["country"], "US")
