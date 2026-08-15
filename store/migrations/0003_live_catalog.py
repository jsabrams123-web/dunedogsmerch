from django.db import migrations, models


LIVE_PRODUCTS = [
    {
        "name": "Dune Dogs Black Logo Tee",
        "price": 40,
        "category": "T-Shirts",
        "description": "Black Dune Dogs logo tee.",
        "image": "uploads/products/black_logo_tee.png",
    },
    {
        "name": "Dune Dogs White Logo Tee",
        "price": 40,
        "category": "T-Shirts",
        "description": "White Dune Dogs globe-logo tee.",
        "image": "uploads/products/white_logo_tee.png",
    },
    {
        "name": "Dune Dogs Blue Corduroy Hat",
        "price": 35,
        "category": "Hats",
        "description": "Blue corduroy cap with the Dune Dogs globe mark.",
        "image": "uploads/products/blue_corduroy_hat.png",
    },
    {
        "name": "Dune Dogs Cream Rope Hat",
        "price": 35,
        "category": "Hats",
        "description": "Cream rope cap with a brown Dune Dogs globe patch.",
        "image": "uploads/products/cream_rope_hat.png",
    },
]


def set_live_catalog(apps, schema_editor):
    Category = apps.get_model("store", "Category")
    Products = apps.get_model("store", "Products")

    Products.objects.update(is_active=False)
    categories = {
        name: Category.objects.get_or_create(name=name)[0]
        for name in {item["category"] for item in LIVE_PRODUCTS}
    }

    for item in LIVE_PRODUCTS:
        Products.objects.update_or_create(
            name=item["name"],
            defaults={
                "price": item["price"],
                "category": categories[item["category"]],
                "description": item["description"],
                "image": item["image"],
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_seed_products"),
    ]

    operations = [
        migrations.AddField(
            model_name="products",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(set_live_catalog, reverse_code=migrations.RunPython.noop),
    ]
