# Generated by Django 4.2.5 on 2023-11-16 14:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0026_domain_registration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registrar",
            name="iana_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]