# Generated by Django 4.0 on 2022-03-12 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShoppingCart', '0003_remove_shoppingcartitem_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcartitem',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=''),
        ),
    ]
