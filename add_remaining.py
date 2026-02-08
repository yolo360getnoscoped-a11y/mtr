import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile

def parse_name(fullname):
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

students = [
    ('68342110084-9', 'นาย ประเสริฐ ดีงาม'),
    ('68342110091-7', 'นางสาว มานี ขยันเรียน'),
    ('68342110098-5', 'นาย วิชัย เก่งมาก'),
    ('68342110105-3', 'นางสาว สมหญิง รักเรียน'),
    ('68342110112-1', 'นาย สมชาย ใจดี'),
    ('68342110119-9', 'นางสาว กาญจนา ตั้งใจ'),
    ('68342110126-7', 'นาย วรวิทย์ ขยัน'),
    ('68342110133-5', 'นางสาว สุภาพ ดีใจ'),
    ('68342110140-3', 'นาย ธีระ เรียนดี'),
    ('68342110147-1', 'นางสาว อรุณ ดีงาม'),
    ('68342110154-9', 'นาย พงศ์ศักดิ์ ขยันเรียน'),
    ('68342110161-7', 'นางสาว วรรณา เก่งมาก'),
    ('68342110168-5', 'นาย สุเมธ รักเรียน'),
    ('68342110175-3', 'นางสาว ปิยะ ใจดี'),
    ('68342110182-1', 'นาย ธีรศักดิ์ ตั้งใจ'),
    ('68342110189-9', 'นางสาว อรทัย มานะ'),
    ('68342110196-7', 'นาย วิทยา ดีใจ'),
    ('68342110203-5', 'นางสาว กมลชนก เรียนดี'),
    ('68342110210-3', 'นาย ธีรพงษ์ ดีงาม'),
]

created_count = 0
updated_count = 0

for student_id, fullname in students:
    first_name, last_name = parse_name(fullname)
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
        print(f'✓ สร้าง: {username} - {first_name} {last_name}')
    else:
        user.first_name = first_name
        user.last_name = last_name
        user.role = 'student'
        user.save()
        updated_count += 1
        print(f'⚠ อัปเดต: {username} - {first_name} {last_name}')
    
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'student_id': student_id}
    )
    
    if profile.student_id != student_id:
        profile.student_id = student_id
        profile.save()

print(f'\n✅ เสร็จสมบูรณ์! สร้างใหม่ {created_count} คน, อัปเดต {updated_count} คน')

