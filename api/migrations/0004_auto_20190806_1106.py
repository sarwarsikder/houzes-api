# Generated by Django 2.2.2 on 2019-08-06 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_userlocation_angle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlist',
            name='leads_count',
            field=models.IntegerField(default=0),
        ),
    ]
