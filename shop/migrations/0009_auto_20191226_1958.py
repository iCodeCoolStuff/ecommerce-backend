# Generated by Django 2.2.5 on 2019-12-27 00:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_product_new'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imageset',
            old_name='img300x400',
            new_name='img1920x1080',
        ),
        migrations.RenameField(
            model_name='imageset',
            old_name='img500x600',
            new_name='img690x400',
        ),
    ]
