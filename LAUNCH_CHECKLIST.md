# Dune Dogs World Stripe Launch Checklist

The storefront, cart, fixed $7 shipping, Stripe Checkout handoff, and verified Stripe webhook are ready in the codebase. Payment remains disabled until real Stripe and hosting settings are supplied.

## Before Real Fans Can Buy

1. Create and verify the Dune Dogs Stripe account.
2. Add the live Stripe secret key and webhook signing secret in the production host's environment settings.
3. Deploy the site to a public HTTPS domain.
4. Register `https://YOUR-DOMAIN/webhooks/stripe/` in Stripe and subscribe it to:
   - `checkout.session.completed`
   - `checkout.session.async_payment_succeeded`
   - `checkout.session.async_payment_failed`
5. Test a purchase in Stripe test mode, including the flat $7 shipping charge and a cancelled checkout.
6. Configure Stripe tax only after deciding where the band needs to collect it.
7. Set `STRIPE_CHECKOUT_ENABLED=True` only after the live webhook is verified.

## What Is Working Now

- Public storefront pages: home, shop, product detail, cart, and checkout return page
- Product and catalog data in Django
- Session cart with add/remove quantities
- One flat $7 shipping option per Checkout Session
- Signed Stripe webhook that records payment status and shipping details
- Django admin is not exposed on the public site
- Production settings are controlled by environment variables
- Deployment environment example is in `.env.example`

## Hosting Inputs Needed

- A host such as Render, Railway, Fly.io, Heroku, or DigitalOcean
- Domain name
- Production `DJANGO_SECRET_KEY`
- Production `DJANGO_ALLOWED_HOSTS`
- HTTPS enabled
- A persistent production database for Stripe payment records
- Media/image hosting if product images are uploaded through a future owner dashboard

## Public Pages To Polish Before Launch

- Product names and product descriptions
- Product images and sizing
- Shipping / return policy page
- Contact page or support email
- Privacy policy
- Terms of sale

## Important

Never put Stripe secrets in source code or send them in chat. Run the test checkout before sharing the live site with fans.
