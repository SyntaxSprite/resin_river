# Generated by Django 4.2.5 on 2023-12-04 00:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resin_apps', '0002_alter_category_options_alter_items_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='items',
            options={'verbose_name_plural': 'Items'},
        ),
    ]
