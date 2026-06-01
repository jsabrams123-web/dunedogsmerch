# How To Edit The Dune Dogs Site

## Edit Product Names, Prices, Images, And Descriptions

The public site does not expose Django admin anymore, so fans will not see a login page.

For now, the cleanest way to edit product records is to ask Codex to update them, or edit the database from Django code.

Those changes are saved in `db.sqlite3`, the Django database file.

## Edit Homepage Words

Open:

`store/templates/store/index.html`

Common lines to change:

- Hero label: `Official Rock Band Merch`
- Hero title: `Dune Dogs World`
- Hero paragraph under the title
- Button text: `Enter the Store`
- Brand story section words
- Featured merch heading

Save the file and refresh the browser.

## Edit Shop, Cart, Checkout, And Order Confirmation Words

Templates are here:

- Shop page: `store/templates/store/products.html`
- Product detail page: `store/templates/store/product_detail.html`
- Cart page: `store/templates/store/cart.html`
- Checkout page: `store/templates/store/checkout.html`
- Order confirmation page: `store/templates/store/order_confirmation.html`

## Edit Colors, Fonts, Spacing, And Layout

Open:

`store/static/store/style.css`

The main colors are at the top of the file under `:root`.

The current fonts are:

- Display headings: `Bebas Neue`
- Body text: `Space Grotesk`

The font import is in:

`store/templates/store/base.html`

## Edit The Logo Or Photos

The site assets are here:

- Logo: `store/static/store/dunedogs-logo.png`
- Band photo: `store/static/store/dunedogs-band.jpg`
- Merch tee photo: `store/static/store/dunedogs-merch-tee.jpg`

If you replace a file with the same name, refresh the browser to see the update.

## Database-Backed Checkout

The cart is stored in the browser session while shopping.

When a customer submits checkout details, the site saves:

- Customer info into `Customer`
- One `Order` row for each cart item

This is the current foundation for adding Stripe, Shopify, or another payment provider next.
