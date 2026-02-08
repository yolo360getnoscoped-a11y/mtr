# Generated manually
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0006_fix_attendance_record_fields'),
    ]

    operations = [
        # Remove old fields that are no longer used
        migrations.RemoveField(
            model_name='attendancesession',
            name='session_token',
        ),
        migrations.RemoveField(
            model_name='attendancesession',
            name='expires_at',
        ),
        migrations.RemoveField(
            model_name='attendancesession',
            name='created_by',
        ),
    ]

