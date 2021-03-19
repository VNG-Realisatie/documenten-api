# Generated by Django 2.2.4 on 2021-03-19 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0054_merge_20201204_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectinformatieobject',
            name='informatieobject_versie',
            field=models.IntegerField(blank=True, help_text='De versie van het INFORMATIEOBJECT', null=True, verbose_name='informatieobject versie'),
        ),
        migrations.AlterUniqueTogether(
            name='objectinformatieobject',
            unique_together={('informatieobject', 'object', 'informatieobject_versie')},
        ),
    ]