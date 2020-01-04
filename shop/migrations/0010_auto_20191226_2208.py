# Generated by Django 3.0.1 on 2019-12-27 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20191226_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='list_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AddField(
            model_name='product',
            name='on_sale',
            field=models.BooleanField(default=False),
        ),
    ]