# Generated by Django 3.1 on 2020-11-29 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('client_settings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientformelementsettings',
            name='permissions',
            field=models.ManyToManyField(null=True, to='auth.Permission'),
        ),
    ]
