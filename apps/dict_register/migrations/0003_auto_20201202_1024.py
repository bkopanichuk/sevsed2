# Generated by Django 3.1 on 2020-12-02 08:24

import apps.dict_register.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dict_register', '0002_auto_20201202_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatedocument',
            name='template_file',
            field=models.FileField(max_length=500, null=True, upload_to=apps.dict_register.models.get_upload_template_path, verbose_name='Шаблон документу'),
        ),
    ]
