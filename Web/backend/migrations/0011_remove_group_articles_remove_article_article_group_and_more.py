# Generated by Django 4.1.1 on 2022-09-28 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_group_articles_remove_article_article_group_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='articles',
        ),
        migrations.RemoveField(
            model_name='article',
            name='article_group',
        ),
        migrations.AddField(
            model_name='article',
            name='article_group',
            field=models.ManyToManyField(to='backend.group'),
        ),
    ]