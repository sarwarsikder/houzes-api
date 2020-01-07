# Generated by Django 2.2.3 on 2020-01-07 10:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20200102_0437'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailWizardSubsType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=500, null=True)),
                ('days_interval', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'mail_wizard_subs_types',
            },
        ),
        migrations.CreateModel(
            name='MailWizardInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('property', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Property')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subs_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.MailWizardSubsType')),
            ],
            options={
                'db_table': 'mail_wizard_info',
            },
        ),
    ]
