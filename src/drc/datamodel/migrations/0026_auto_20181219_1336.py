# Generated by Django 2.0.9 on 2018-12-19 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("datamodel", "0025_enkelvoudiginformatieobject_verzenddatum")]

    operations = [
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="ontvangstdatum",
            field=models.DateField(
                blank=True,
                help_text="De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.",
                null=True,
                verbose_name="ontvangstdatum",
            ),
        ),
        migrations.AlterField(
            model_name="enkelvoudiginformatieobject",
            name="verzenddatum",
            field=models.DateField(
                blank=True,
                help_text="De datum waarop het INFORMATIEOBJECT verzonden is, zoals deze op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde informatieobject kan niet tegelijk inkomend en uitgaand zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt.",
                null=True,
                verbose_name="verzenddatum",
            ),
        ),
    ]
