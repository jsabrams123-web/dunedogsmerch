from django.db import migrations


PRODUCTS = [
    {
        "name": "Dune Dogs Blue Corduroy Hat",
        "price": 35,
        "category": "Hats",
        "description": "Blue corduroy Dune Dogs World cap with a clean embroidered hit for rehearsals, shows, and the everyday band uniform.",
        "image": "uploads/products/blue_corduroy_hat.jpg",
    },
    {
        "name": "Dune Dogs Cream Rope Hat",
        "price": 35,
        "category": "Hats",
        "description": "Cream rope hat with a Dune Dogs patch, built like a merch-table staple from the band's visual world.",
        "image": "uploads/products/cream_rope_hat.jpg",
    },
    {
        "name": "Dune Dogs Classic White Tee",
        "price": 30,
        "category": "T-Shirts",
        "description": "Classic white tee with a small Dune Dogs mark, made for fans who want the band energy without overplaying it.",
        "image": "uploads/products/classic_white_tee.jpg",
    },
    {
        "name": "Dune Dogs Navy Letter Tee",
        "price": 30,
        "category": "T-Shirts",
        "description": "White tee with the bold navy Dune Dogs wordmark, pulled straight from the band's current graphic universe.",
        "image": "uploads/products/navy_letter_tee.jpg",
    },
    {
        "name": "Dune Dogs Blue Hoodie",
        "price": 60,
        "category": "Sweatshirts",
        "description": "Blue hoodie with front Dune Dogs artwork, a heavyweight layer for late load-outs, cold venues, and daily rotation.",
        "image": "uploads/products/blue_hoodie.jpg",
    },
    {
        "name": "Dune Dogs Black Hoodie",
        "price": 60,
        "category": "Sweatshirts",
        "description": "Black hoodie with the Dune Dogs globe mark, dark, loud, and ready for the show-night uniform.",
        "image": "uploads/products/black_hoodie.jpg",
    },
]


def seed_products(apps, schema_editor):
    Category = apps.get_model("store", "Category")
    Products = apps.get_model("store", "Products")

    categories = {
        name: Category.objects.get_or_create(name=name)[0]
        for name in ["Hats", "T-Shirts", "Sweatshirts"]
    }

    for item in PRODUCTS:
        Products.objects.update_or_create(
            name=item["name"],
            defaults={
                "price": item["price"],
                "category": categories[item["category"]],
                "description": item["description"],
                "image": item["image"],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0001_initial_schema"),
    ]

    operations = [
        migrations.RunPython(seed_products, reverse_code=migrations.RunPython.noop),
    ]
