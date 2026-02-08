#!/usr/bin/env python
"""
Script to add remaining 18 students
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile

def parse_thai_name(fullname):
    """Parse Thai name to extract first name and last name"""
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

def add_remaining_students():
    """Add remaining 18 students"""
    print("=" * 60)
    print("กำลังเพิ่มนักเรียนที่เหลือ 18 คน")
    print("=" * 60)
    
    # ข้อมูลนักเรียนที่เหลือ 18 คน
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
    error_count = 0
    
    print(f"\nกำลังเพิ่มนักเรียน {len(students_data)} คน...")
    print("=" * 60)
    
    for idx, student_data in enumerate(students_data, start=1):
        try:
            student_id = student_data['student_id']
            fullname = student_data['fullname']
            
            # Parse Thai name
            first_name, last_name = parse_thai_name(fullname)
            
            # Generate username from student_id (remove hyphen)
            username = student_id.replace('-', '')
            
            # Check if user already exists
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
                print(f"  [{idx:2d}] ✓ สร้าง: {username} - {first_name} {last_name} ({student_id})")
            else:
                # Update existing user
                user.first_name = first_name
                user.last_name = last_name
                user.role = 'student'
                user.save()
                updated_count += 1
                print(f"  [{idx:2d}] ⚠ อัปเดต: {username} - {first_name} {last_name} ({student_id})")
            
            # Create or update profile
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': student_id
                }
            )
            
            if not profile_created and profile.student_id != student_id:
                profile.student_id = student_id
                profile.save()
                
        except Exception as e:
            error_count += 1
            print(f"  [{idx:2d}] ❌ ข้อผิดพลาด: {student_data.get('student_id', 'N/A')} - {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ เสร็จสมบูรณ์!")
    print("=" * 60)
    print(f"\nสรุป:")
    print(f"  - สร้างใหม่: {created_count} คน")
    print(f"  - อัปเดต: {updated_count} คน")
    print(f"  - ข้อผิดพลาด: {error_count} คน")
    print(f"  - รวม: {created_count + updated_count} คน")
    print(f"\nรหัสผ่านเริ่มต้นสำหรับนักเรียนทั้งหมด: changeme123")
    print(f"\nตอนนี้มีนักเรียนทั้งหมด {User.objects.filter(role='student').count()} คนในระบบ!")

if __name__ == '__main__':
    add_remaining_students()

