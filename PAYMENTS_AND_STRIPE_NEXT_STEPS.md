# Payments And Stripe Next Steps

The fan flow is now:

1. A fan adds one or more live Dune Dogs pieces to the cart.
2. The site calculates the merchandise subtotal and one flat $7 shipping charge.
3. The fan is redirected to Stripe's hosted Checkout page.
4. Stripe sends a signed event back to the site after payment.
5. The site stores the payment result and shipping details in `StripeOrder`.

## Remaining launch decisions

- Complete the Stripe business profile and banking details.
- Decide which countries can receive merchandise. The code starts with `US` only.
- Set up tax collection only where it is required.
- Decide where fulfilled orders are managed and how shipping labels are purchased.
- Add customer support, shipping, return, privacy, and terms pages before the public launch.

The payment route is intentionally Stripe-only. There is no Shopify dependency in the checkout flow.
