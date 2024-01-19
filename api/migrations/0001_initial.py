# Generated by Django 4.2.7 on 2024-01-18 00:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('username', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(choices=[('quiz', 'Quiz'), ('exam', 'Exam')], max_length=50)),
                ('description', models.TextField()),
                ('lesson_path', models.TextField()),
                ('no_of_questions', models.IntegerField()),
                ('date_created', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question_Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_no', models.IntegerField()),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=64)),
                ('length', models.IntegerField()),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.assessment')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.question_type')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_no', models.IntegerField()),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.section')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_no', models.IntegerField()),
                ('option', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.question')),
            ],
        ),
        migrations.CreateModel(
            name='Learning_Outcomes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('learning_outcome', models.CharField(max_length=256)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.section')),
            ],
        ),
    ]
