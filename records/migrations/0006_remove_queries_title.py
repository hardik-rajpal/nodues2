# Generated by Django 4.0.3 on 2022-03-31 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0005_alter_queries_document_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='queries',
            name='title',
        ),
    ]