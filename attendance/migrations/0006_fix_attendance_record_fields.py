# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_add_session_datetime'),
    ]

    operations = [
        # Rename scanned_at to checked_in_at
        migrations.RenameField(
            model_name='attendancerecord',
            old_name='scanned_at',
            new_name='checked_in_at',
        ),
        # Remove updated_by field if it exists
        migrations.RemoveField(
            model_name='attendancerecord',
            name='updated_by',
        ),
        # Remove updated_at field if it exists
        migrations.RemoveField(
            model_name='attendancerecord',
            name='updated_at',
        ),
        # Update notes field to allow null
        migrations.AlterField(
            model_name='attendancerecord',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        # Update checked_in_at to allow null
        migrations.AlterField(
            model_name='attendancerecord',
            name='checked_in_at',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        # Update ordering
        migrations.AlterModelOptions(
            name='attendancerecord',
            options={'ordering': ['-checked_in_at'], 'verbose_name': 'บันทึกการเข้าเรียน', 'verbose_name_plural': 'บันทึกการเข้าเรียน'},
        ),
    ]

