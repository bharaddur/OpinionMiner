# Generated by Django 4.1.3 on 2022-12-03 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweets',
            name='sentiment',
            field=models.TextField(default='def', max_length=10),
            preserve_default=False,
        ),
    ]
