# Generated by Django 4.1.3 on 2022-12-15 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominer', '0013_tweets_context_annotations_tweets_entities'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweets',
            name='author_id',
            field=models.TextField(blank=True, max_length=280, null=True),
        ),
    ]
