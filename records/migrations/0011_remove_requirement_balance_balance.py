# Generated by Django 4.0.3 on 2022-05-24 03:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0010_alter_queries_status_check'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requirement',
            name='balance',
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('isMonetary', models.BooleanField(default=True)),
                ('comment', models.TextField(default='None', max_length=500)),
                ('requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='records.requirement')),
            ],
        ),
    ]