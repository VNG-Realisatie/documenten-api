# Generated by Django 3.2.13 on 2023-01-19 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0059_auto_20221205_1326"),
    ]

    operations = [
        migrations.AddField(
            model_name="verzending",
            name="telefoonnummer",
            field=models.CharField(
                blank=True,
                help_text="Faxnummer van de afzender.",
                max_length=15,
                null=True,
                verbose_name="faxnummer",
            ),
        ),
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="taal",
            field=models.CharField(
                help_text="Een ISO 639-2/B taalcode waarin de inhoud van het INFORMATIEOBJECT is vastgelegd. Voorbeeld: `dut`. Zie: https://www.iso.org/standard/4767.html",
                max_length=3,
            ),
        ),
    ]
