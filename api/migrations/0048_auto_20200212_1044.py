# Generated by Django 2.2.3 on 2020-02-12 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0047_user_photo_thumb'),
    ]

    operations = [
        migrations.AddField(
            model_name='upgradeprofile',
            name='refId',
            field=models.CharField(default=None, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='upgradeprofile',
            name='subscriptionId',
            field=models.CharField(default=None, max_length=500, null=True),
        ),
    ]
