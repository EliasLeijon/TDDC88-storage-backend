# Generated by Django 4.1.1 on 2022-10-05 13:15

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('expectedWait', models.PositiveSmallIntegerField(default=0)),
                ('orderTime', models.DateTimeField(default=datetime.datetime.now)),
                ('ofArticle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.article')),
                ('toStorageUnit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.storageunit')),
            ],
        ),
        migrations.CreateModel(
            name='CentralStorageSpace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.PositiveSmallIntegerField(default=0)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.article')),
            ],
        ),
    ]