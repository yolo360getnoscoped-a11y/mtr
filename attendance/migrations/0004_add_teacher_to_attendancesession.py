# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_leaverequest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancesession',
            name='teacher',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_sessions',
                to=settings.AUTH_USER_MODEL,
                null=True,  # Allow null temporarily
                blank=True
            ),
        ),
        # Update existing records if any
        migrations.RunSQL(
            # Set teacher from section.teacher if section has teacher
            sql="UPDATE attendance_attendancesession SET teacher_id = (SELECT teacher_id FROM academic_section WHERE academic_section.id = attendance_attendancesession.section_id) WHERE teacher_id IS NULL;",
            reverse_sql="UPDATE attendance_attendancesession SET teacher_id = NULL;"
        ),
        # Make field required
        migrations.AlterField(
            model_name='attendancesession',
            name='teacher',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_sessions',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

