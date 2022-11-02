# Generated by Django 4.1.1 on 2022-11-02 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_article_refill_unit_article_takeout_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='storageunit',
            name='cost_center',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.costcenter'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='time_of_transaction',
            field=models.DateField(auto_now_add=True),
        ),
    ]