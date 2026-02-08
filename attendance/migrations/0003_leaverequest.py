# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0001_initial'),
        ('attendance', '0002_auto_20251105_1142'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('sick', 'ลาป่วย'), ('personal', 'ลากิจ'), ('social', 'กิจการเพื่อสังคม'), ('other', 'อื่นๆ')], default='sick', max_length=20)),
                ('leave_date', models.DateField()),
                ('reason', models.TextField()),
                ('supporting_document', models.FileField(blank=True, null=True, upload_to='leave_documents/')),
                ('status', models.CharField(choices=[('pending', 'รออนุมัติ'), ('approved', 'อนุมัติ'), ('rejected', 'ไม่อนุมัติ')], default='pending', max_length=20)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='academic.section')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leave_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

