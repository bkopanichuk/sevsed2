# Generated by Django 3.1 on 2020-12-02 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('l_core', '0001_initial'),
        ('dict_register', '0003_auto_20201202_1024'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='templatedocument',
            unique_together={('related_model_name', 'organization')},
        ),
    ]