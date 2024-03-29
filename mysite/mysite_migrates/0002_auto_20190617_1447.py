# Generated by Django 2.1 on 2019-06-17 06:47

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.ForeignKey(default=datetime.datetime(2019, 6, 17, 6, 47, 42, 255515, tzinfo=utc), on_delete=django.db.models.deletion.CASCADE, to='blog.Category'),
            preserve_default=False,
        ),
    ]
