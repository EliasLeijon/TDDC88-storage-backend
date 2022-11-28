# Generated by Django 4.1.1 on 2022-11-28 12:49

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('lio_id', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100, null=True)),
                ('price', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=30)),
                ('Z41', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('input', models.CharField(choices=[('ml', 'Millilitres'), ('cl', 'Centilitres'), ('dl', 'Decilitres'), ('l', 'Litres'), ('mm', 'Millimetres'), ('cm', 'Centimetres'), ('m', 'Metres'), ('pieces', 'Pieces'), ('crates', 'Crates'), ('bottles', 'Bottles')], default='ml', max_length=100)),
                ('output', models.CharField(choices=[('ml', 'Millilitres'), ('cl', 'Centilitres'), ('dl', 'Decilitres'), ('l', 'Litres'), ('mm', 'Millimetres'), ('cm', 'Centimetres'), ('m', 'Metres'), ('pieces', 'Pieces'), ('crates', 'Crates'), ('bottles', 'Bottles')], default='ml', max_length=100)),
                ('output_per_input', models.IntegerField(default=1, null=True)),
                ('supplier_article_nr', models.CharField(max_length=15, null=True)),
                ('alternative_articles', models.ManyToManyField(blank=True, to='backend.article')),
            ],
            options={
                'permissions': (('post_article', 'Can create an article'), ('put_article', 'Can edit an article'), ('delete_article_new', 'Can delete an article')),
            },
        ),
        migrations.CreateModel(
            name='CostCenter',
            fields=[
                ('name', models.CharField(max_length=30)),
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='GroupInfo',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estimated_delivery_date', models.DateTimeField()),
                ('delivery_date', models.DateTimeField(null=True)),
                ('order_date', models.DateTimeField(default=datetime.datetime.now)),
                ('order_state', models.CharField(choices=[('order placed', 'Order Placed'), ('delivered', 'Delivered')], default='order placed', max_length=100)),
            ],
            options={
                'permissions': (('get_order', 'Can get orders from database'),),
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('building', models.CharField(max_length=30)),
                ('floor', models.CharField(max_length=30)),
                ('cost_center', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.costcenter')),
            ],
            options={
                'permissions': (('get_storage_cost', 'Can see storage cost'), ('get_storage_value', 'Can see storage value'), ('return_to_storage', 'Can return article to storage'), ('add_input_unit', 'Can ad an input unit to storage')),
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, null=True)),
                ('supplier_number', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('barcode_id', models.CharField(max_length=255, null=True, unique=True)),
                ('nfc_id', models.CharField(max_length=256, null=True, unique=True)),
                ('cost_center', models.ManyToManyField(to='backend.costcenter')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.PositiveSmallIntegerField(default=0)),
                ('time_of_transaction', models.DateTimeField(auto_now_add=True, null=True)),
                ('unit', models.CharField(choices=[('input', 'Input'), ('output', 'Output')], default='output', max_length=100)),
                ('operation', models.CharField(choices=[('takeout', 'Takeout'), ('return', 'Return'), ('replenish', 'Replenish'), ('adjust', 'Adjust')], default='return', max_length=100)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.article')),
                ('attribute_cost_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.costcenter')),
                ('by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.storage')),
            ],
            options={
                'permissions': (('get_all_transaction', 'Can get all transactions'), ('get_transaction_by_id', 'Can get a transaction by id'), ('get_user_transactions', 'Can get a users transactions'), ('replenish', 'Can replenish articles to compartment'), ('move_article', 'Can move articles between compartments')),
            },
        ),
        migrations.CreateModel(
            name='OrderedArticle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=None)),
                ('unit', models.CharField(choices=[('input', 'Input'), ('output', 'Output')], default='input', max_length=10)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.article')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='to_storage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.storage'),
        ),
        migrations.CreateModel(
            name='InputOutput',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('input_unit_name', models.CharField(max_length=30)),
                ('output_unit_name', models.CharField(max_length=30)),
                ('output_unit_per_input_unit', models.PositiveIntegerField(default=0)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.article')),
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
        migrations.AddField(
            model_name='article',
            name='article_group',
            field=models.ManyToManyField(to='backend.groupinfo'),
        ),
        migrations.AddField(
            model_name='article',
            name='supplier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.supplier'),
        ),
        migrations.CreateModel(
            name='AlternativeArticleName',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.article')),
            ],
        ),
        migrations.CreateModel(
            name='Compartment',
            fields=[
                ('id', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('order_point', models.PositiveSmallIntegerField(default=0)),
                ('standard_order_amount', models.PositiveSmallIntegerField(default=0)),
                ('maximal_capacity', models.PositiveSmallIntegerField(default=0)),
                ('amount', models.PositiveSmallIntegerField(default=0)),
                ('placement', models.CharField(max_length=30, null=True)),
                ('article', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.article')),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.storage')),
            ],
            options={
                'permissions': (),
                'unique_together': {('storage', 'article')},
            },
        ),
    ]
