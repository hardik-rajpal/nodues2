# Generated by Django 4.0.3 on 2022-03-31 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_alter_queries_document_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queries',
            name='document_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]