# Generated by Django 5.1.7 on 2025-04-02 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authSys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
