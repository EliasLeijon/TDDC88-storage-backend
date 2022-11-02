# Generated by Django 4.1.1 on 2022-11-01 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_storagespace_placement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagespace',
            name='article',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.article'),
        ),
    ]