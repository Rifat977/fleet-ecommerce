# Generated by Django 5.1.4 on 2025-02-27 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0003_rename_address_companysetting_address_line_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companysetting',
            name='shipping_fee',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Enter shipping fee as extra charge', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='companysetting',
            name='tax',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Enter tax as a percentage (%)', max_digits=5, null=True),
        ),
    ]
