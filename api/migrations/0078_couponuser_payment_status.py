# Generated by Django 2.2.3 on 2020-07-22 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0077_couponuser_affiliate_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponuser',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
    ]
