# Generated by Django 4.1.1 on 2022-11-01 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_alter_inputoutput_inputunitname_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='storagespace',
            name='placement',
            field=models.CharField(max_length=30, null=True),
        ),
    ]