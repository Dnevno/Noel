# Generated by Django 4.2.19 on 2025-03-28 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myhealth', '0008_remove_userdata_email_remove_userdata_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='displayed_name',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
