# Generated by Django 5.1.7 on 2025-04-02 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authSys', '0003_alter_member_last_login_alter_member_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='password',
            field=models.CharField(max_length=250),
        ),
    ]
