# Generated by Django 4.0.3 on 2022-03-31 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0006_remove_queries_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='queries',
            name='response',
            field=models.TextField(default='', max_length=500),
        ),
    ]
