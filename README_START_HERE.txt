DUNE DOGS DJANGO MERCH SITE - READY TO FILM

This is the customized Dune Dogs version of the Django e-commerce app.
It includes:
- Dune Dogs World homepage, shop page, cart, and Stripe checkout return page
- White and navy clothing-brand styling while keeping the official band merch identity
- A deliberately small catalog: black logo tee, white logo tee, blue corduroy hat, and cream rope hat
- Database-backed products, categories, local cart data, and Stripe payment records
- Session cart with add/remove quantities
- Stripe-hosted checkout with a verified payment webhook endpoint

Fan-facing site:
- Open the store at http://127.0.0.1:8000/ when running locally.
- There is no public admin/login page in the fan storefront.

How to personally edit words and details:
- Homepage words: store/templates/store/index.html
- Shop page words: store/templates/store/products.html
- Product detail words: store/templates/store/product_detail.html
- Cart words: store/templates/store/cart.html
- Colors, spacing, fonts, and layout: store/static/store/style.css
- Product names, prices, images, and descriptions: the Django database records
- Live/retired product visibility: the Product "is active" field in the Django database
- Stripe setup: STRIPE_SETUP.md and .env.example

How to run on Mac:
1. Open this folder in VS Code.
2. Open Terminal in VS Code.
3. Run:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 manage.py runserver
4. Open:
   http://127.0.0.1:8000/

Video talking point:
"I customized the original Django e-commerce application into a Dune Dogs World merch store. It now runs as a deliberately small four-piece band drop, with real product photography, a functioning cart, and Stripe-hosted checkout ready for secure payments."
