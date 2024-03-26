# Generated by Django 5.0.3 on 2024-03-25 22:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('database_id', models.AutoField(primary_key=True, serialize=False)),
                ('database_name', models.CharField(max_length=255)),
                ('access_key', models.CharField(blank=True, max_length=255, null=True)),
                ('connection_string', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('access_token', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('refresh_token', models.CharField(blank=True, default=None, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('conversation_id', models.AutoField(primary_key=True, serialize=False)),
                ('database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.database')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.user')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.conversation')),
            ],
        ),
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('prompt_id', models.AutoField(primary_key=True, serialize=False)),
                ('prompt_data', models.TextField()),
                ('database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.database')),
            ],
        ),
    ]