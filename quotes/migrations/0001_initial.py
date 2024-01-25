# Generated by Django 4.2.9 on 2024-01-23 07:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FxPriceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('exchange', models.CharField(max_length=50)),
                ('section', models.CharField(max_length=50)),
                ('instrument', models.CharField(blank=True, max_length=50, null=True)),
                ('price', models.FloatField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(max_length=255)),
                ('point_size', models.FloatField()),
                ('currency', models.CharField(max_length=3)),
                ('asset_class', models.CharField(max_length=50)),
                ('slippage', models.FloatField()),
                ('per_block', models.FloatField(blank=True, null=True)),
                ('percentage', models.FloatField(blank=True, null=True)),
                ('per_trade', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RollCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.CharField(max_length=50)),
                ('current_contract', models.CharField(blank=True, max_length=50, null=True)),
                ('next_contract', models.CharField(blank=True, max_length=50, null=True)),
                ('carry_contract', models.CharField(blank=True, max_length=50, null=True)),
                ('timestamp', models.DateTimeField()),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quotes.instrument')),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.CharField(max_length=50)),
                ('section', models.CharField(max_length=50)),
                ('contract', models.CharField(blank=True, max_length=50, null=True)),
                ('sectype', models.CharField(blank=True, max_length=50, null=True)),
                ('secid', models.CharField(blank=True, max_length=50, null=True)),
                ('open_price', models.FloatField(blank=True, default=0, null=True)),
                ('high_price', models.FloatField(blank=True, default=0, null=True)),
                ('low_price', models.FloatField(blank=True, default=0, null=True)),
                ('close_price', models.FloatField(blank=True, default=0, null=True)),
                ('volume', models.FloatField(blank=True, default=0, null=True)),
                ('timestamp', models.DateTimeField()),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quotes.instrument')),
            ],
        ),
        migrations.CreateModel(
            name='MultiplePriceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('carry', models.FloatField()),
                ('carry_contract', models.CharField(max_length=10)),
                ('price', models.FloatField()),
                ('price_contract', models.CharField(max_length=10)),
                ('forward', models.FloatField()),
                ('forward_contract', models.CharField(max_length=10)),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quotes.instrument')),
                ('quote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quotes.quote')),
            ],
        ),
        migrations.CreateModel(
            name='AdjustedPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('price', models.FloatField()),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quotes.instrument')),
            ],
        ),
    ]
