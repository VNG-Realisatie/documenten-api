# Generated by Django 2.0.6 on 2018-08-15 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("datamodel", "0011_merge_20180815_1426")]

    operations = [
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="beschrijving",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT.",
                max_length=1000,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="link",
            field=models.URLField(
                blank=True,
                default="",
                help_text="De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is.",
            ),
            preserve_default=False,
        ),
    ]
