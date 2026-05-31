DUNE DOGS DJANGO MERCH SITE - READY TO FILM

This is the customized Dune Dogs version of the Django e-commerce app.
It already includes:
- 3 categories: Hats, T-Shirts, Sweatshirts
- 6 products from the Dune Dogs merch mockups
- Prices: T-Shirts $30, Hats $35, Sweatshirts $60
- Sample customers and orders
- Updated Dune Dogs styled homepage, shop page, cart, and orders page
- Database-backed checkout that saves customers and orders

How to personally edit words and details:
- Open EDITING_GUIDE.md in this folder.
- Product names, prices, images, and descriptions can be edited in the Django admin.
- Homepage text lives in store/templates/store/index.html.
- Colors, fonts, spacing, and layout live in store/static/store/style.css.

Admin login:
Username: admin
Password: Admin12345!

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
5. Admin panel:
   http://127.0.0.1:8000/admin/

Database checkout:
1. Add a product to the cart.
2. Go to Cart.
3. Click Checkout.
4. Fill in the form and click Save Order.
5. The saved order appears on the Orders page.

Video talking point:
"I customized the original Django e-commerce application into a Dune Dogs merch store. I updated the homepage, styling, product cards, categories, product names, prices, cart page, checkout page, and orders page while keeping the Django database functionality working."
