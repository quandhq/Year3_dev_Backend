# Generated by Django 4.1.1 on 2023-12-20 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_registration_mac'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('timezone', models.CharField(max_length=255)),
                ('timezone_offset', models.IntegerField()),
                ('current_dt', models.BigIntegerField()),
                ('current_sunrise', models.BigIntegerField()),
                ('current_sunset', models.BigIntegerField()),
                ('current_temp', models.FloatField()),
                ('current_feels_like', models.FloatField()),
                ('current_pressure', models.IntegerField()),
                ('current_humidity', models.IntegerField()),
                ('current_dew_point', models.FloatField()),
                ('current_uvi', models.FloatField()),
                ('current_clouds', models.IntegerField()),
                ('current_visibility', models.IntegerField()),
                ('current_wind_speed', models.FloatField()),
                ('current_wind_deg', models.IntegerField()),
                ('current_wind_gust', models.FloatField(blank=True, null=True)),
                ('current_weather', models.JSONField()),
            ],
        ),
        migrations.RemoveField(
            model_name='controlsetpoint',
            name='aim',
        ),
        migrations.RemoveField(
            model_name='controlsetpoint',
            name='option',
        ),
        migrations.RemoveField(
            model_name='controlsetpoint',
            name='value',
        ),
        migrations.AddField(
            model_name='controlsetpoint',
            name='device_type',
            field=models.TextField(db_column='device_type', null=True),
        ),
        migrations.AddField(
            model_name='controlsetpoint',
            name='end_time',
            field=models.BigIntegerField(db_column='end_time', null=True),
        ),
        migrations.AddField(
            model_name='controlsetpoint',
            name='power',
            field=models.IntegerField(db_column='power', null=True),
        ),
        migrations.AddField(
            model_name='controlsetpoint',
            name='start_time',
            field=models.BigIntegerField(db_column='start_time', null=True),
        ),
        migrations.AddField(
            model_name='controlsetpoint',
            name='status',
            field=models.IntegerField(db_column='status', null=True),
        ),
        migrations.AddField(
            model_name='controlsetpoint',
            name='temp',
            field=models.IntegerField(db_column='temp', null=True),
        ),
    ]
