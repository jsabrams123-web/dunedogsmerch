# Stripe Checkout Setup

The Dune Dogs site keeps the storefront and cart in Django, then sends a fan to Stripe's hosted Checkout page for payment. Stripe returns the fan to the site after checkout and sends a signed webhook that records the payment result.

## 1. Create the Stripe account

Create and verify the Dune Dogs Stripe account. Add the Dune Dogs World logo and brand colors in the Stripe Dashboard so the hosted payment page looks like part of the store.

## 2. Add test settings first

For the local preview, enter these values in the private `.env` file in the project folder. The preview launcher reads that file automatically. In production, add the same values in the host's environment settings. Do not put live secrets in source code or chat.

```text
STRIPE_CHECKOUT_ENABLED=False
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SHIPPING_COUNTRIES=US
STRIPE_SERVICE_FEE_PERCENT=2.9
STRIPE_SERVICE_FEE_FIXED_CENTS=30
```

The checkout creates the current cart server-side, using the prices stored in Django. It includes one fixed $7 shipping option per order, regardless of the number of pieces.

The customer-facing service fee is calculated on the merchandise and shipping total using a gross-up of the standard domestic-card rate (2.9% + 30 cents). This means the displayed service fee covers that baseline processor charge instead of silently reducing the order payout. Confirm the actual rate for the Dune Dogs Stripe account and the rules where you sell before using this charge in live mode; international cards and custom Stripe plans can have different fees.

Install the newly added Stripe dependency once in a normal Mac terminal before restarting the preview:

```text
/Users/jamesabrams/Downloads/ready_ecommerce-2/.venv/bin/python -m pip install -r requirements.txt
```

For a local end-to-end test, Stripe also needs a webhook tunnel. Install the Stripe CLI, sign in, then run:

```text
stripe listen --forward-to http://127.0.0.1:8013/webhooks/stripe/
```

Copy the `whsec_...` value it prints into `STRIPE_WEBHOOK_SECRET`, set `STRIPE_CHECKOUT_ENABLED=True`, then restart the preview.

## 3. Deploy to a public HTTPS domain

Stripe needs a public HTTPS URL for payment webhooks. Once the site is deployed, create a Stripe webhook endpoint at:

```text
https://YOUR-DOMAIN/webhooks/stripe/
```

Subscribe it to:

- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`
- `checkout.session.async_payment_failed`

Copy the endpoint signing secret into `STRIPE_WEBHOOK_SECRET`.

## 4. Test the whole path

With test keys in place, set `STRIPE_CHECKOUT_ENABLED=True` and make one test purchase. Confirm that Stripe shows the payment and the Django `StripeOrder` record contains the session ID, amount, shipping address, and a paid payment status. Also test the cancel link returning to the cart.

## 5. Go live

Replace the test secret key and webhook signing secret with their live-mode counterparts, verify the webhook endpoint again, then enable `STRIPE_CHECKOUT_ENABLED=True` in the live environment.

Stripe handles payment collection. Tax registration, tax configuration, shipping fulfillment, customer support, and refund policy decisions still belong to the Dune Dogs team.
