# Generated by Django 3.2.13 on 2022-09-29 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0056_auto_20220704_0857"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="indicatie_gebruiksrecht",
            field=models.BooleanField(
                blank=True,
                default=None,
                help_text="Indicatie of er beperkingen gelden aangaande het gebruik van het informatieobject anders dan raadpleging. Dit veld mag `null` zijn om aan te geven dat de indicatie nog niet bekend is. Als de indicatie gezet is, dan kan je de gebruiksrechten die van toepassing zijn raadplegen via de GEBRUIKSRECHTen resource.",
                null=True,
                verbose_name="indicatie gebruiksrecht",
            ),
        ),
    ]
