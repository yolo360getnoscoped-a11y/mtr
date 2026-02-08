import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile

def parse_thai_name(fullname):
    if fullname.startswith('นางสาว'):
        name = fullname.replace('นางสาว', '').strip()
    elif fullname.startswith('นาย'):
        name = fullname.replace('นาย', '').strip()
    else:
        name = fullname.strip()
    
    parts = name.split()
    if len(parts) >= 2:
        return parts[0], ' '.join(parts[1:])
    elif len(parts) == 1:
        return parts[0], ''
    else:
        return name, ''

students_data = [
    {'student_id': '68342110084-9', 'fullname': 'นาย ประเสริฐ ดีงาม'},
    {'student_id': '68342110091-7', 'fullname': 'นางสาว มานี ขยันเรียน'},
    {'student_id': '68342110098-5', 'fullname': 'นาย วิชัย เก่งมาก'},
    {'student_id': '68342110105-3', 'fullname': 'นางสาว สมหญิง รักเรียน'},
    {'student_id': '68342110112-1', 'fullname': 'นาย สมชาย ใจดี'},
    {'student_id': '68342110119-9', 'fullname': 'นางสาว กาญจนา ตั้งใจ'},
    {'student_id': '68342110126-7', 'fullname': 'นาย วรวิทย์ ขยัน'},
    {'student_id': '68342110133-5', 'fullname': 'นางสาว สุภาพ ดีใจ'},
    {'student_id': '68342110140-3', 'fullname': 'นาย ธีระ เรียนดี'},
    {'student_id': '68342110147-1', 'fullname': 'นางสาว อรุณ ดีงาม'},
    {'student_id': '68342110154-9', 'fullname': 'นาย พงศ์ศักดิ์ ขยันเรียน'},
    {'student_id': '68342110161-7', 'fullname': 'นางสาว วรรณา เก่งมาก'},
    {'student_id': '68342110168-5', 'fullname': 'นาย สุเมธ รักเรียน'},
    {'student_id': '68342110175-3', 'fullname': 'นางสาว ปิยะ ใจดี'},
    {'student_id': '68342110182-1', 'fullname': 'นาย ธีรศักดิ์ ตั้งใจ'},
    {'student_id': '68342110189-9', 'fullname': 'นางสาว อรทัย มานะ'},
    {'student_id': '68342110196-7', 'fullname': 'นาย วิทยา ดีใจ'},
    {'student_id': '68342110203-5', 'fullname': 'นางสาว กมลชนก เรียนดี'},
    {'student_id': '68342110210-3', 'fullname': 'นาย ธีรพงษ์ ดีงาม'},
]

created_count = 0
updated_count = 0

for student_data in students_data:
    student_id = student_data['student_id']
    fullname = student_data['fullname']
    first_name, last_name = parse_thai_name(fullname)
    username = student_id.replace('-', '')
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'role': 'student',
            'is_staff': False,
            'email': f'{username}@student.example.com'
        }
    )
    
    if created:
        user.set_password('changeme123')
        user.save()
        created_count += 1
        print(f"✓ สร้าง: {username} - {first_name} {last_name}")
    else:
        user.first_name = first_name
        user.last_name = last_name
        user.role = 'student'
        user.save()
        updated_count += 1
        print(f"⚠ อัปเดต: {username} - {first_name} {last_name}")
    
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'student_id': student_id}
    )
    
    if profile.student_id != student_id:
        profile.student_id = student_id
        profile.save()

print(f"\n✅ เสร็จสมบูรณ์! สร้างใหม่ {created_count} คน, อัปเดต {updated_count} คน")

