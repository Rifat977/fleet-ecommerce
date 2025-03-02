# Generated by Django 5.1.4 on 2025-03-02 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_address_user_street_address_user_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Discount in amount', max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_cost',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Shipping cost in amount', max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Tax in amount', max_digits=10),
        ),
    ]
