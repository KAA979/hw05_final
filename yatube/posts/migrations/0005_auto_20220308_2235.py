# Generated by Django 2.2.16 on 2022-03-08 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220304_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Выберите группу', max_length=200, verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='groups', to='posts.Group'),
        ),
    ]
