# Generated by Django 5.1.4 on 2025-02-20 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_adminprofile_options_alter_cupon_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cupon',
            name='discount',
            field=models.IntegerField(default=0),
        ),
    ]
