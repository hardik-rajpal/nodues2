# Generated by Django 4.0.3 on 2022-03-30 17:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('records', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('last_ping', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('roll_no', models.CharField(blank=True, max_length=30, null=True)),
                ('ldap_id', models.CharField(blank=True, max_length=50, null=True)),
                ('profile_pic', models.URLField(blank=True, null=True)),
                ('contact_no', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('degree', models.CharField(blank=True, max_length=200, null=True)),
                ('degree_name', models.CharField(blank=True, max_length=200, null=True)),
                ('join_year', models.CharField(blank=True, max_length=5, null=True)),
                ('graduation_year', models.CharField(blank=True, max_length=5, null=True)),
                ('hostel', models.CharField(blank=True, max_length=100, null=True)),
                ('room', models.CharField(blank=True, max_length=30, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdminProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='records.department')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.userprofile')),
            ],
        ),
    ]
