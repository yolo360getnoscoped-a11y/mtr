# Generated manually
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_add_teacher_to_attendancesession'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancesession',
            name='session_datetime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        # Update existing records: combine session_date and session_time
        migrations.RunSQL(
            sql="""
            UPDATE attendance_attendancesession 
            SET session_datetime = (
                session_date + session_time
            )::timestamp
            WHERE session_datetime IS NULL;
            """,
            reverse_sql="UPDATE attendance_attendancesession SET session_datetime = NULL;"
        ),
        # Make field required
        migrations.AlterField(
            model_name='attendancesession',
            name='session_datetime',
            field=models.DateTimeField(),
        ),
    ]

