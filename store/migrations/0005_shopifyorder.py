from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_products_shopify_variant_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopifyOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("shopify_order_id", models.CharField(max_length=80, unique=True)),
                ("order_name", models.CharField(blank=True, max_length=80)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("financial_status", models.CharField(blank=True, max_length=50)),
                ("fulfillment_status", models.CharField(blank=True, max_length=50)),
                ("total_price", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("currency", models.CharField(blank=True, max_length=8)),
                ("line_items", models.JSONField(default=list)),
                ("received_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Shopify orders",
            },
        ),
    ]
