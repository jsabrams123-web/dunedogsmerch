# How To Edit The Dune Dogs Site

## Edit Product Names, Prices, Images, And Descriptions

The public site does not expose Django admin anymore, so fans will not see a login page.

For now, the cleanest way to edit product records is to ask Codex to update them, or edit the database from Django code.

Those changes are saved in `db.sqlite3`, the Django database file.

## Edit Homepage Words

Open:

`store/templates/store/index.html`

The homepage layout and copy live in:

`store/templates/store/index.html`

Save the file and refresh the browser.

## Edit Shop, Cart, And Checkout Words

Templates are here:

- Shop page: `store/templates/store/products.html`
- Product detail page: `store/templates/store/product_detail.html`
- Cart page: `store/templates/store/cart.html`
- Stripe return page: `store/templates/store/stripe_success.html`

## Edit Colors, Fonts, Spacing, And Layout

Open:

`store/static/store/style.css`

The main colors are at the top of the file under `:root`.

The current fonts are Raleway for display type and Inter for body copy.

The font import is in:

`store/templates/store/base.html`

## Edit The Logo Or Photos

The site assets are here:

- Header logo: `store/static/store/dunedogs-world-logo.png`
- Homepage band photo: `store/static/store/dunedogs-rail.jpg`
- Product photos: `store/media/uploads/products/`

If you replace a file with the same name, refresh the browser to see the update.

## Stripe Checkout

The cart is stored in the browser session while shopping. When checkout is enabled, the site creates a Stripe-hosted Checkout Session and keeps a matching `StripeOrder` record in the database. Payment status only updates from Stripe's signed webhook.

Stripe keys and the webhook secret belong in the hosting environment, never in the code or browser.
