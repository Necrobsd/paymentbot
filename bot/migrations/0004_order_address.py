# Generated by Django 2.0.7 on 2018-07-26 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20180726_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(default='', max_length=254, verbose_name='Адрес доставки'),
        ),
    ]
