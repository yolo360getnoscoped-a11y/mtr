#!/usr/bin/env python
"""
Script to add students to bis3r1 section directly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile
from academic.models import Section, Enrollment, Course

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

def add_students_to_bis3r1():
    """Add students to bis3r1 section"""
    print("=" * 80)
    print("เพิ่มนักเรียนเข้าในกลุ่มเรียน 123456789 - กลุ่ม bis3r1")
    print("=" * 80)
    
    # ค้นหากลุ่มเรียน bis3r1 (รายวิชา 123456789)
    section = Section.objects.filter(
        section_number__iexact='bis3r1',
        course__course_code='123456789'
    ).select_related('course', 'semester', 'teacher').first()
    
    if not section:
        print("\n❌ ไม่พบกลุ่มเรียน bis3r1 (รายวิชา 123456789)")
        print("\nกลุ่มเรียนที่มีในระบบ (รายวิชา 123456789):")
        sections = Section.objects.filter(course__course_code='123456789')
        for s in sections:
            print(f"  - {s.course.course_code} - กลุ่ม {s.section_number} (ID: {s.id})")
        return
    
    print(f"\n✓ พบกลุ่มเรียน: {section}")
    print(f"   รายวิชา: {section.course.course_code} - {section.course.course_name}")
    print(f"   ภาคเรียน: {section.semester}")
    print(f"   อาจารย์: {section.teacher.get_full_name() if section.teacher else 'ยังไม่กำหนด'}")
    print(f"   Section ID: {section.id}")
    
    # ข้อมูลนักเรียน 30 คน
    students_data = [
        {'student_id': '68342110008-1', 'fullname': 'นางสาว จรรยพร ทิดี'},
        {'student_id': '68342110014-9', 'fullname': 'นาย กิตติพัฒน์ โสระมรรค'},
        {'student_id': '68342110021-7', 'fullname': 'นางสาว ชนัญธิดา ทองค่า'},
        {'student_id': '68342110028-5', 'fullname': 'นาย พนารักษ์ พงษ์เกษม'},
        {'student_id': '68342110035-3', 'fullname': 'นางสาว รัตนา ใจดี'},
        {'student_id': '68342110042-1', 'fullname': 'นาย สุทธิพงษ์ ขยันเรียน'},
        {'student_id': '68342110049-9', 'fullname': 'นางสาว อรทัย ตั้งใจ'},
        {'student_id': '68342110056-7', 'fullname': 'นาย วิทยา มานะ'},
        {'student_id': '68342110063-5', 'fullname': 'นางสาว กมลชนก ดีใจ'},
        {'student_id': '68342110070-3', 'fullname': 'นาย ธีรพงษ์ ขยัน'},
        {'student_id': '68342110077-1', 'fullname': 'นางสาว สุดา เรียนดี'},
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
    
    created_users = 0
    updated_users = 0
    added_enrollments = 0
    skipped_enrollments = 0
    errors = []
    
    print(f"\nกำลังเพิ่มนักเรียน {len(students_data)} คน...")
    print("-" * 80)
    
    for idx, student_data in enumerate(students_data, start=1):
        try:
            student_id = student_data['student_id']
            fullname = student_data['fullname']
            
            # Parse Thai name
            first_name, last_name = parse_thai_name(fullname)
            
            # Generate username from student_id (remove hyphen)
            username = student_id.replace('-', '')
            
            # Check if user already exists
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'student',
                    'is_staff': False,
                    'email': f'{username}@student.example.com'
                }
            )
            
            if user_created:
                user.set_password('changeme123')
                user.save()
                created_users += 1
                print(f"  [{idx:2d}] ✓ สร้างผู้ใช้: {username} - {first_name} {last_name}")
            else:
                # Update existing user
                user.first_name = first_name
                user.last_name = last_name
                user.role = 'student'
                user.save()
                updated_users += 1
                print(f"  [{idx:2d}] ⚠ อัปเดตผู้ใช้: {username} - {first_name} {last_name}")
            
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
            
            # Add enrollment to bis3r1
            enrollment, enrollment_created = Enrollment.objects.get_or_create(
                student=user,
                section=section,
                defaults={'status': 'enrolled'}
            )
            
            if enrollment_created:
                added_enrollments += 1
                print(f"      ✓ เพิ่มการลงทะเบียน (Enrollment ID: {enrollment.id})")
            else:
                skipped_enrollments += 1
                print(f"      ⚠ ข้าม (ลงทะเบียนแล้ว - Enrollment ID: {enrollment.id})")
                
        except Exception as e:
            errors.append(f"{student_id}: {str(e)}")
            print(f"  [{idx:2d}] ❌ ข้อผิดพลาด: {student_id} - {str(e)}")
    
    # สรุปผล
    print("\n" + "=" * 80)
    print("✅ เสร็จสมบูรณ์!")
    print("=" * 80)
    print(f"\nสรุปผล:")
    print(f"  - สร้างผู้ใช้ใหม่: {created_users} คน")
    print(f"  - อัปเดตผู้ใช้: {updated_users} คน")
    print(f"  - เพิ่มการลงทะเบียน: {added_enrollments} คน")
    print(f"  - ข้าม (ลงทะเบียนแล้ว): {skipped_enrollments} คน")
    print(f"  - ข้อผิดพลาด: {len(errors)} คน")
    
    if errors:
        print(f"\nข้อผิดพลาด:")
        for error in errors:
            print(f"  - {error}")
    
    # ตรวจสอบข้อมูลในฐานข้อมูล
    print(f"\n" + "=" * 80)
    print("ตรวจสอบข้อมูลในฐานข้อมูล")
    print("=" * 80)
    
    final_enrollments = Enrollment.objects.filter(section=section, status='enrolled')
    print(f"\nจำนวนนักเรียนที่ลงทะเบียนในกลุ่มเรียน bis3r1: {final_enrollments.count()} คน")
    print(f"จำนวนรับ: {section.capacity} คน")
    print(f"ว่าง: {section.capacity - final_enrollments.count()} คน")
    
    print(f"\nรายชื่อนักเรียน 10 คนแรก:")
    for idx, enrollment in enumerate(final_enrollments.select_related('student')[:10], 1):
        student = enrollment.student
        student_id = student.profile.student_id if hasattr(student, 'profile') and student.profile.student_id else student.username
        print(f"  {idx:2d}. {student_id} - {student.get_full_name() or student.username} (Enrollment ID: {enrollment.id})")
    
    print("\n" + "=" * 80)
    print("ตอนนี้สามารถไปตรวจสอบใน Django Admin ได้แล้ว!")
    print("URL: http://127.0.0.1:8000/admin/academic/enrollment/")
    print("=" * 80)

if __name__ == '__main__':
    add_students_to_bis3r1()

