# Generated by Django 4.1.3 on 2022-12-03 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominer', '0003_alter_tweets_sentiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweets',
            name='user',
            field=models.TextField(default='user', max_length=100),
            preserve_default=False,
        ),
    ]
