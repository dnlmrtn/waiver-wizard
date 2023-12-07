# Generated by Django 4.2.6 on 2023-12-07 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Games',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('home_team', models.CharField(max_length=50)),
                ('away_team', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yahoo_id', models.CharField(max_length=6)),
                ('name', models.CharField(max_length=100)),
                ('team', models.CharField(max_length=50)),
                ('positions', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('gtd', 'GTD'), ('out', 'O'), ('injured', 'INJ'), ('healthy', 'H')], default='active', max_length=10)),
                ('time_of_last_update', models.DateTimeField(auto_now=True)),
                ('points_per_game', models.DecimalField(decimal_places=2, max_digits=5)),
                ('assists_per_game', models.DecimalField(decimal_places=2, max_digits=5)),
                ('rebounds_per_game', models.DecimalField(decimal_places=2, max_digits=5)),
                ('steals_per_game', models.DecimalField(decimal_places=2, max_digits=5)),
                ('blocks_per_game', models.DecimalField(decimal_places=2, max_digits=5)),
                ('to_per_game', models.DecimalField(decimal_places=2, max_digits=5)),
                ('fan_pts', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
    ]
