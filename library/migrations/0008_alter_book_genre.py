# Generated by Django 5.2.1 on 2025-06-05 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='genre',
            field=models.CharField(choices=[('F', 'Fiction')], default='NOT_SET', max_length=50),
        ),
    ]
