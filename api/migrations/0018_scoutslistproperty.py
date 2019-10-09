# Generated by Django 2.2.3 on 2019-08-30 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_user_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoutsListProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Property')),
                ('scout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Scout')),
            ],
            options={
                'db_table': 'scouts_properties',
            },
        ),
    ]
