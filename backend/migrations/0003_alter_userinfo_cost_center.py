# Generated by Django 4.1.1 on 2022-09-28 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_costcenter_userinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='cost_center',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.costcenter'),
        ),
    ]
