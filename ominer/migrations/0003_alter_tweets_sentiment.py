# Generated by Django 4.1.3 on 2022-12-03 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominer', '0002_tweets_sentiment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweets',
            name='sentiment',
            field=models.TextField(max_length=15),
        ),
    ]