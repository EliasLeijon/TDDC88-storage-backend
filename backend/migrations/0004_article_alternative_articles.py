# Generated by Django 4.1.1 on 2022-09-27 12:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_article_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='alternative_articles',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.article'),
        ),
    ]
