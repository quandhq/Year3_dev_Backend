# Generated by Django 4.1.1 on 2023-08-31 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='x_axis',
            field=models.IntegerField(db_column='x_axis', default=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='y_axis',
            field=models.IntegerField(db_column='y_axis', default=2),
            preserve_default=False,
        ),
    ]
