# Generated migration for unified profile
from django.db import migrations, models
import django.db.models.deletion


def migrate_profiles_to_unified(apps, schema_editor):
    """
    Migrate data from separate profiles to unified UserProfile
    """
    User = apps.get_model('accounts', 'User')
    UserProfile = apps.get_model('accounts', 'UserProfile')
    
    # Try to get old profile models - they may not exist if this is a fresh install
    try:
        AdminProfile = apps.get_model('accounts', 'AdminProfile')
        # Migrate Admin profiles
        for admin_profile in AdminProfile.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=admin_profile.user)
            profile.admin_department = admin_profile.department
            profile.admin_notes = admin_profile.notes
            profile.save()
    except LookupError:
        # AdminProfile model doesn't exist, skip migration
        pass
    
    try:
        TeacherProfile = apps.get_model('accounts', 'TeacherProfile')
        # Migrate Teacher profiles
        for teacher_profile in TeacherProfile.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=teacher_profile.user)
            profile.teacher_employee_id = teacher_profile.employee_id
            profile.teacher_faculty = teacher_profile.faculty
            profile.teacher_university_email = teacher_profile.university_email
            profile.teacher_department = teacher_profile.department
            profile.teacher_office = teacher_profile.office
            profile.save()
    except LookupError:
        # TeacherProfile model doesn't exist, skip migration
        pass
    
    try:
        StudentProfile = apps.get_model('accounts', 'StudentProfile')
        # Migrate Student profiles
        for student_profile in StudentProfile.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=student_profile.user)
            profile.student_id = student_profile.student_id
            profile.student_year = student_profile.year
            profile.student_major = student_profile.major
            profile.student_university_email = student_profile.university_email
            profile.save()
    except LookupError:
        # StudentProfile model doesn't exist, skip migration
        pass


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - recreate separate profiles from unified profile
    """
    User = apps.get_model('accounts', 'User')
    UserProfile = apps.get_model('accounts', 'UserProfile')
    AdminProfile = apps.get_model('accounts', 'AdminProfile')
    TeacherProfile = apps.get_model('accounts', 'TeacherProfile')
    StudentProfile = apps.get_model('accounts', 'StudentProfile')
    
    for profile in UserProfile.objects.all():
        user = profile.user
        
        # Recreate AdminProfile
        if user.is_admin():
            AdminProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': profile.admin_department,
                    'notes': profile.admin_notes
                }
            )
        
        # Recreate TeacherProfile
        elif user.is_teacher():
            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': profile.teacher_employee_id,
                    'faculty': profile.teacher_faculty,
                    'university_email': profile.teacher_university_email,
                    'department': profile.teacher_department,
                    'office': profile.teacher_office
                }
            )
        
        # Recreate StudentProfile
        elif user.is_student():
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': profile.student_id,
                    'year': profile.student_year,
                    'major': profile.student_major,
                    'university_email': profile.student_university_email
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_teacherprofile_faculty_and_more'),
    ]

    operations = [
        # Create UserProfile model
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_department', models.CharField(blank=True, max_length=100, null=True, verbose_name='หน่วยงาน (Admin)')),
                ('admin_notes', models.TextField(blank=True, null=True, verbose_name='หมายเหตุ (Admin)')),
                ('teacher_employee_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='รหัสพนักงาน')),
                ('teacher_faculty', models.CharField(blank=True, max_length=100, null=True, verbose_name='คณะ')),
                ('teacher_university_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='อีเมลมหาวิทยาลัย (Teacher)')),
                ('teacher_department', models.CharField(blank=True, max_length=100, null=True, verbose_name='ภาควิชา')),
                ('teacher_office', models.CharField(blank=True, max_length=200, null=True, verbose_name='ห้องทำงาน')),
                ('student_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='รหัสนักศึกษา')),
                ('student_year', models.IntegerField(blank=True, null=True, verbose_name='ปีการศึกษา')),
                ('student_major', models.CharField(blank=True, max_length=100, null=True, verbose_name='สาขา')),
                ('student_university_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='อีเมลมหาวิทยาลัย (Student)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='accounts.user', verbose_name='ผู้ใช้')),
            ],
            options={
                'verbose_name': 'โปรไฟล์ผู้ใช้',
                'verbose_name_plural': 'โปรไฟล์ผู้ใช้',
            },
        ),
        # Migrate data
        migrations.RunPython(migrate_profiles_to_unified, reverse_migration),
    ]

