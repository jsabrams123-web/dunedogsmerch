# Dune Dogs World Launch Checklist

This site is now ready as a custom Django storefront foundation. It can show merch, collect cart items, and save customer/order rows to the database.

It is not ready to take real fan payments until Shopify or Stripe is connected.

## What Is Working Now

- Public storefront pages: home, shop, product detail, cart, checkout details, order confirmation
- Product data in Django database
- Cart stored in the shopper session
- Checkout form saves customer and order rows
- Django admin is not exposed on the public site
- There is no public order list route, so customer order details are not exposed
- Production settings can be controlled with environment variables
- Dependencies are listed in `requirements.txt`
- Deployment environment example is in `.env.example`
- Product database seed data is in Django migrations for fresh deploys

## Before Real Fans Can Buy

Choose one checkout system:

1. Shopify checkout, recommended for merch
2. Stripe checkout, better if Django remains the main order system

## Shopify Launch Inputs Needed

Send these when ready:

- Shopify store domain, for example `dunedogs.myshopify.com`
- Storefront API access token
- Shopify product variant ID for each product in Django
- Final product names, prices, and inventory
- Shipping/tax setup inside Shopify

Recommended fan flow:

1. Fan shops on the custom Django site.
2. Django creates a Shopify cart with the current items.
3. Fan is redirected to Shopify checkout.
4. Shopify handles payment, taxes, shipping, order emails, and fulfillment.

## Hosting Inputs Needed

Choose where this should live:

- Render
- Railway
- Fly.io
- Heroku
- DigitalOcean
- Another host

You will also need:

- Domain name
- Production `DJANGO_SECRET_KEY`
- Production `DJANGO_ALLOWED_HOSTS`
- HTTPS enabled
- Real database plan if Django keeps production orders
- Media/image hosting if product images are uploaded through a future owner dashboard

## Public Pages To Polish Before Launch

- Homepage hero wording
- Product names and product descriptions
- Product images and sizing
- Shipping / return policy page
- Contact page or support email
- Privacy policy
- Terms of sale

## Important

Do not send real fans to the current checkout until payment integration is connected. Right now it saves order details only; it does not charge money.
