# Generated by Django 5.1.4 on 2025-03-09 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0005_pos_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='pos',
            name='sub_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='pos',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Discount in percentage', max_digits=5),
        ),
        migrations.AlterField(
            model_name='pos',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Tax in percentage', max_digits=5),
        ),
    ]
