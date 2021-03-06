# Generated by Django 4.0.3 on 2022-03-30 17:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Requirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0)),
                ('comment', models.TextField(default='None', max_length=500)),
                ('time_posted', models.DateTimeField(default=django.utils.timezone.now)),
                ('roll_number', models.CharField(max_length=11)),
                ('department', models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.CASCADE, to='records.department')),
            ],
        ),
        migrations.CreateModel(
            name='Queries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('document_id', models.CharField(max_length=50)),
                ('status_check', models.BooleanField(default=False)),
                ('time_posted', models.DateTimeField()),
                ('requirement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='records.requirement')),
            ],
        ),
    ]
