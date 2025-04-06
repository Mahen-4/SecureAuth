# Generated by Django 5.1.7 on 2025-04-04 15:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authSys', '0005_member_groups_member_is_superuser_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='digiCode',
            fields=[
                ('id_member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('code', models.IntegerField(unique=True)),
                ('expiration_datetime', models.DateTimeField()),
            ],
        ),
    ]
