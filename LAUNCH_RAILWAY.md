# Dune Dogs World Launch

This project is configured for a small Railway deployment with Railway Postgres.

1. Push this project, including the `media/` catalog imagery, to the GitHub repository used for the storefront.
2. In Railway, create a project from that GitHub repository and add a PostgreSQL service.
3. In the web service's Variables page, add `DATABASE_URL=${{Postgres.DATABASE_URL}}` and the production variables below. Do not add the `.env` file to GitHub.

```text
DJANGO_SECRET_KEY=<a new long random value>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<railway-domain>,<your-custom-domain>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<railway-domain>,https://<your-custom-domain>
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
STRIPE_CHECKOUT_ENABLED=True
STRIPE_SECRET_KEY=<Stripe test key while reviewing, then Stripe live key at launch>
STRIPE_WEBHOOK_SECRET=<Stripe webhook signing secret for the public site>
STRIPE_SHIPPING_COUNTRIES=US
STRIPE_SERVICE_FEE_PERCENT=2.9
STRIPE_SERVICE_FEE_FIXED_CENTS=30
```

4. Generate Railway's public domain, then add the custom domain when it is ready. Update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` with the final domains.
5. In Stripe, add the public webhook endpoint `https://<your-domain>/webhooks/stripe/` and subscribe to `checkout.session.completed`, `checkout.session.async_payment_succeeded`, and `checkout.session.async_payment_failed`. Use that endpoint's signing secret for `STRIPE_WEBHOOK_SECRET`.
6. Complete one test purchase on the public Railway URL. Only then replace the Stripe test key with the live secret key and repeat the public webhook setup in Stripe live mode.

Railway's `railway.toml` runs migrations before each deployment and checks `/healthz/` before releasing the site.
