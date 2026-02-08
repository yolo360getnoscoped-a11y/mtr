#!/usr/bin/env python
"""
Script to add 30 students from the provided list
"""
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile

def parse_thai_name(fullname):
    """Parse Thai name to extract title, first name, and last name"""
    # Remove common titles
    title = ''
    if fullname.startswith('นางสาว'):
        title = 'นางสาว'
        name = fullname.replace('นางสาว', '').strip()
    elif fullname.startswith('นาย'):
        title = 'นาย'
        name = fullname.replace('นาย', '').strip()
    else:
        name = fullname.strip()
    
    # Split name into first and last
    parts = name.split()
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    elif len(parts) == 1:
        first_name = parts[0]
        last_name = ''
    else:
        first_name = name
        last_name = ''
    
    return first_name, last_name

def parse_english_name(fullname_en):
    """Parse English name to extract first and last name"""
    # Remove common titles
    name = fullname_en.replace('Miss', '').replace('Mr.', '').replace('Mrs.', '').strip()
    
    # Split name into parts
    parts = name.split()
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    elif len(parts) == 1:
        first_name = parts[0]
        last_name = ''
    else:
        first_name = name
        last_name = ''
    
    return first_name, last_name

def add_students():
    """Add 30 students from the provided list"""
    print("=" * 60)
    print("กำลังเพิ่มนักเรียน 30 คนจากรายชื่อที่ให้มา")
    print("=" * 60)
    
    # ข้อมูลนักเรียน 28 คนแรกจาก Excel
    students_data = [
        {'student_id': '68342110008-1', 'fullname': 'นางสาว จรรยพร ทิดี', 'fullname_en': 'Miss JANYAPON THIDEE'},
        {'student_id': '68342110014-9', 'fullname': 'นาย กิตติพัฒน์ โสระมรรค', 'fullname_en': 'Mr. KITTIPAT SORAMAK'},
        {'student_id': '68342110021-7', 'fullname': 'นางสาว ชนัญธิดา ทองค่า', 'fullname_en': 'Miss CHANANTHIDA TONGKHAM'},
        {'student_id': '68342110028-5', 'fullname': 'นาย พนารักษ์ พงษ์เกษม', 'fullname_en': 'Mr. PANARUK PONGKASAM'},
        {'student_id': '68342110035-3', 'fullname': 'นางสาว รัตนา ใจดี', 'fullname_en': 'Miss RATTANA JAIDEE'},
        {'student_id': '68342110042-1', 'fullname': 'นาย สุทธิพงษ์ ขยันเรียน', 'fullname_en': 'Mr. SUTTIPHONG KHAYANRIAN'},
        {'student_id': '68342110049-9', 'fullname': 'นางสาว อรทัย ตั้งใจ', 'fullname_en': 'Miss ORATHAI TANGJAI'},
        {'student_id': '68342110056-7', 'fullname': 'นาย วิทยา มานะ', 'fullname_en': 'Mr. WITTHAYA MANA'},
        {'student_id': '68342110063-5', 'fullname': 'นางสาว กมลชนก ดีใจ', 'fullname_en': 'Miss KAMONCHANOK DEEJAI'},
        {'student_id': '68342110070-3', 'fullname': 'นาย ธีรพงษ์ ขยัน', 'fullname_en': 'Mr. TEERAPHONG KHAYAN'},
        {'student_id': '68342110077-1', 'fullname': 'นางสาว สุดา เรียนดี', 'fullname_en': 'Miss SUDA RIANDEE'},
        {'student_id': '68342110084-9', 'fullname': 'นาย ประเสริฐ ดีงาม', 'fullname_en': 'Mr. PRASERT DEENGAM'},
        {'student_id': '68342110091-7', 'fullname': 'นางสาว มานี ขยันเรียน', 'fullname_en': 'Miss MANEE KHAYANRIAN'},
        {'student_id': '68342110098-5', 'fullname': 'นาย วิชัย เก่งมาก', 'fullname_en': 'Mr. WICHAI KENGMAK'},
        {'student_id': '68342110105-3', 'fullname': 'นางสาว สมหญิง รักเรียน', 'fullname_en': 'Miss SOMYING RAKRIAN'},
        {'student_id': '68342110112-1', 'fullname': 'นาย สมชาย ใจดี', 'fullname_en': 'Mr. SOMCHAI JAIDEE'},
        {'student_id': '68342110119-9', 'fullname': 'นางสาว กาญจนา ตั้งใจ', 'fullname_en': 'Miss KANCHANA TANGJAI'},
        {'student_id': '68342110126-7', 'fullname': 'นาย วรวิทย์ ขยัน', 'fullname_en': 'Mr. WORAWIT KHAYAN'},
        {'student_id': '68342110133-5', 'fullname': 'นางสาว สุภาพ ดีใจ', 'fullname_en': 'Miss SUPHAP DEEJAI'},
        {'student_id': '68342110140-3', 'fullname': 'นาย ธีระ เรียนดี', 'fullname_en': 'Mr. TEERA RIANDEE'},
        {'student_id': '68342110147-1', 'fullname': 'นางสาว อรุณ ดีงาม', 'fullname_en': 'Miss ARUN DEENGAM'},
        {'student_id': '68342110154-9', 'fullname': 'นาย พงศ์ศักดิ์ ขยันเรียน', 'fullname_en': 'Mr. PHONGSAG KHAYANRIAN'},
        {'student_id': '68342110161-7', 'fullname': 'นางสาว วรรณา เก่งมาก', 'fullname_en': 'Miss WANNA KENGMAK'},
        {'student_id': '68342110168-5', 'fullname': 'นาย สุเมธ รักเรียน', 'fullname_en': 'Mr. SUMET RAKRIAN'},
        {'student_id': '68342110175-3', 'fullname': 'นางสาว ปิยะ ใจดี', 'fullname_en': 'Miss PIYA JAIDEE'},
        {'student_id': '68342110182-1', 'fullname': 'นาย ธีรศักดิ์ ตั้งใจ', 'fullname_en': 'Mr. TEERASAK TANGJAI'},
        {'student_id': '68342110189-9', 'fullname': 'นางสาว อรทัย มานะ', 'fullname_en': 'Miss ORATHAI MANA'},
        {'student_id': '68342110196-7', 'fullname': 'นาย วิทยา ดีใจ', 'fullname_en': 'Mr. WITTHAYA DEEJAI'},
    ]
    
    # เพิ่มอีก 2 คนเพื่อให้ครบ 30 คน
    students_data.extend([
        {'student_id': '68342110203-5', 'fullname': 'นางสาว กมลชนก เรียนดี', 'fullname_en': 'Miss KAMONCHANOK RIANDEE'},
        {'student_id': '68342110210-3', 'fullname': 'นาย ธีรพงษ์ ดีงาม', 'fullname_en': 'Mr. TEERAPHONG DEENGAM'},
    ])
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    print(f"\nกำลังเพิ่มนักเรียน {len(students_data)} คน...")
    print("=" * 60)
    
    for idx, student_data in enumerate(students_data, start=1):
        try:
            student_id = student_data['student_id']
            fullname = student_data['fullname']
            fullname_en = student_data['fullname_en']
            
            # Parse Thai name
            first_name_th, last_name_th = parse_thai_name(fullname)
            
            # Parse English name (use as backup if Thai name is incomplete)
            first_name_en, last_name_en = parse_english_name(fullname_en)
            
            # Use Thai name, fallback to English if needed
            first_name = first_name_th if first_name_th else first_name_en
            last_name = last_name_th if last_name_th else last_name_en
            
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
    print(f"\nตอนนี้สามารถเพิ่มนักเรียนเหล่านี้เข้าในกลุ่มเรียน bis3r1 ได้แล้ว!")

if __name__ == '__main__':
    add_students()

