# Generated by Django 4.2.4 on 2023-09-05 11:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_rename_creted_at_comment_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='followers',
            new_name='follower',
        ),
    ]
