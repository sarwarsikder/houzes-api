# Generated by Django 2.2.3 on 2019-12-30 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_auto_20191230_0740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getneighborhood',
            name='status',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
