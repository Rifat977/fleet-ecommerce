# Generated by Django 5.1.4 on 2025-02-01 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_product_colors_alter_product_seo_keywords'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('hex_code', models.CharField(help_text='Hex color code, e.g., #FF5733', max_length=7, unique=True)),
            ],
            options={
                'verbose_name': 'Color',
                'verbose_name_plural': '           Colors',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Size',
                'verbose_name_plural': '           Sizes',
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='product',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='product',
            name='colors',
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='colors', to='core.color'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sizes', to='core.size'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Brand',
        ),
    ]
