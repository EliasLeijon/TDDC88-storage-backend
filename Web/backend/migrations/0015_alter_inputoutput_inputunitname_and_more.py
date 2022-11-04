# Generated by Django 4.1.1 on 2022-11-03 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0014_storageunit_cost_center_alter_transaction_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputoutput',
            name='inputUnitName',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='inputoutput',
            name='outputUnitName',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='inputoutput',
            name='outputUnitPerInputUnit',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
