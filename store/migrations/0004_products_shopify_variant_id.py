from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0003_live_catalog"),
    ]

    operations = [
        migrations.AddField(
            model_name="products",
            name="shopify_variant_id",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
    ]
