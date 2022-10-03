# Generated by Django 4.1.1 on 2022-10-03 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('backend', '0017_remove_article_storagecomponent'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupInfo',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.RenameModel(
            old_name='storageComponent',
            new_name='storageSpace',
        ),
        migrations.RenameModel(
            old_name='Storage',
            new_name='StorageUnit',
        ),
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
        migrations.AlterField(
            model_name='article',
            name='article_group',
            field=models.ManyToManyField(to='backend.groupinfo'),
        ),
    ]
