# Payments And Shopify Next Steps

The database checkout is working now:

1. The shopper adds products to the cart.
2. The shopper fills out the checkout form.
3. Django saves customer and order rows to `db.sqlite3`.
4. The order appears on `/orders/`.

That is the right foundation for payment integration.

## Recommended Shopify Path

Use Shopify as the real checkout and payment system.

Flow:

1. Create products and variants in Shopify.
2. Store each Shopify variant ID in the Django product record.
3. When the customer checks out, Django sends the cart lines to Shopify Storefront API.
4. Shopify returns a checkout URL.
5. Django redirects the customer to Shopify checkout.
6. Shopify handles payment, tax, shipping, and the final Shopify order.

Needed from Shopify:

- Shopify store domain, like `your-store.myshopify.com`
- Storefront API access token
- Shopify product variant IDs for each merch item

Official Shopify docs:

- `cartCreate` mutation: https://shopify.dev/docs/api/storefront/latest/mutations/cartCreate
- Cart `checkoutUrl`: https://shopify.dev/docs/api/storefront/latest/objects/Cart

## Stripe Alternative

Use Stripe if you want Django to stay as the main store database and only outsource payment.

Flow:

1. Customer submits checkout.
2. Django creates a Stripe Checkout Session.
3. Django redirects to Stripe.
4. Stripe sends a webhook back after payment succeeds.
5. Django marks the local order as paid.

Needed from Stripe:

- Stripe secret key
- Stripe webhook signing secret
- A success URL and cancel URL

Official Stripe docs:

- Checkout Sessions overview: https://docs.stripe.com/payments/checkout-sessions
- Checkout Sessions API: https://docs.stripe.com/api/checkout/sessions

## Important Choice

Do not build Shopify checkout and Stripe checkout at the same time unless there is a specific reason.

For a merch store, Shopify is usually the stronger next move because it can own:

- Payments
- Inventory
- Shipping
- Taxes
- Order emails
- Fulfillment workflow

Django can stay as the custom band storefront and brand experience.
