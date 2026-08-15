from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_shopifyorder"),
    ]

    operations = [
        migrations.CreateModel(
            name="StripeOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stripe_checkout_session_id", models.CharField(max_length=255, unique=True)),
                ("payment_intent_id", models.CharField(blank=True, max_length=255)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("payment_status", models.CharField(default="pending", max_length=30)),
                ("subtotal_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("shipping_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("total_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("currency", models.CharField(default="usd", max_length=8)),
                ("shipping_name", models.CharField(blank=True, max_length=120)),
                ("shipping_address", models.JSONField(default=dict)),
                ("line_items", models.JSONField(default=list)),
                ("received_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Stripe orders",
            },
        ),
    ]
