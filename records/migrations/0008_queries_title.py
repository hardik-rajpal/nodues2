# Generated by Django 4.0.3 on 2022-03-31 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0007_queries_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='queries',
            name='title',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]