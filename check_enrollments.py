#!/usr/bin/env python
"""
Script to check enrollment data and relationships
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile
from academic.models import Section, Enrollment, Course

def check_enrollments():
    """Check enrollment data and relationships"""
    print("=" * 80)
    print("ตรวจสอบข้อมูลการลงทะเบียนและความสัมพันธ์")
    print("=" * 80)
    
    # 1. ตรวจสอบกลุ่มเรียน bis3r1 (รายวิชา 123456789)
    print("\n1. ตรวจสอบกลุ่มเรียน bis3r1 (รายวิชา 123456789)")
    print("-" * 80)
    
    section = Section.objects.filter(
        section_number__iexact='bis3r1',
        course__course_code='123456789'
    ).first()
    
    if not section:
        print("❌ ไม่พบกลุ่มเรียน bis3r1 (รายวิชา 123456789)")
        print("\nกลุ่มเรียนที่มีในระบบ:")
        all_sections = Section.objects.filter(course__course_code='123456789')[:10]
        for s in all_sections:
            print(f"  - {s.course.course_code} - กลุ่ม {s.section_number} (ID: {s.id})")
    else:
        print(f"✓ พบกลุ่มเรียน: {section}")
        print(f"   รายวิชา: {section.course.course_code} - {section.course.course_name}")
        print(f"   ภาคเรียน: {section.semester}")
        print(f"   อาจารย์: {section.teacher.get_full_name() if section.teacher else 'ยังไม่กำหนด'}")
        print(f"   จำนวนรับ: {section.capacity}")
        
        # ตรวจสอบการลงทะเบียน
        enrollments = Enrollment.objects.filter(section=section)
        print(f"\n   การลงทะเบียนทั้งหมด: {enrollments.count()} คน")
        
        enrolled = enrollments.filter(status='enrolled')
        print(f"   - ลงทะเบียน: {enrolled.count()} คน")
        print(f"   - ถอน: {enrollments.filter(status='withdrawn').count()} คน")
        print(f"   - เรียนจบ: {enrollments.filter(status='completed').count()} คน")
        
        if enrolled.exists():
            print(f"\n   รายชื่อนักเรียนที่ลงทะเบียน:")
            for idx, enrollment in enumerate(enrolled.select_related('student', 'student__profile')[:10], 1):
                student = enrollment.student
                student_id = student.profile.student_id if hasattr(student, 'profile') and student.profile.student_id else student.username
                print(f"   {idx:2d}. {student_id} - {student.get_full_name() or student.username} ({student.username})")
        else:
            print("\n   ⚠ ไม่มีนักเรียนลงทะเบียนในกลุ่มเรียนนี้")
    
    # 2. ตรวจสอบนักเรียนที่ควรจะอยู่ในระบบ
    print("\n\n2. ตรวจสอบนักเรียนในระบบ")
    print("-" * 80)
    
    # รายชื่อที่ควรจะมี
    expected_student_ids = [
        '68342110008-1', '68342110014-9', '68342110021-7', '68342110028-5',
        '68342110035-3', '68342110042-1', '68342110049-9', '68342110056-7',
        '68342110063-5', '68342110070-3', '68342110077-1', '68342110084-9',
        '68342110091-7', '68342110098-5', '68342110105-3', '68342110112-1',
        '68342110119-9', '68342110126-7', '68342110133-5', '68342110140-3',
        '68342110147-1', '68342110154-9', '68342110161-7', '68342110168-5',
        '68342110175-3', '68342110182-1', '68342110189-9', '68342110196-7',
        '68342110203-5', '68342110210-3',
    ]
    
    found_count = 0
    missing_count = 0
    enrolled_count = 0
    not_enrolled_count = 0
    
    print(f"ตรวจสอบ {len(expected_student_ids)} คน...")
    
    for student_id in expected_student_ids:
        username = student_id.replace('-', '')
        user = User.objects.filter(username=username, role='student').first()
        
        if user:
            found_count += 1
            # ตรวจสอบ profile
            if hasattr(user, 'profile'):
                profile_student_id = user.profile.student_id if user.profile.student_id else 'N/A'
            else:
                profile_student_id = 'ไม่มี Profile'
            
            # ตรวจสอบการลงทะเบียนใน bis3r1
            if section:
                enrollment = Enrollment.objects.filter(
                    student=user,
                    section=section,
                    status='enrolled'
                ).first()
                
                if enrollment:
                    enrolled_count += 1
                    print(f"  ✓ {student_id} - {user.get_full_name() or user.username} (ลงทะเบียนแล้ว)")
                else:
                    not_enrolled_count += 1
                    print(f"  ⚠ {student_id} - {user.get_full_name() or user.username} (ยังไม่ลงทะเบียน)")
            else:
                print(f"  ✓ {student_id} - {user.get_full_name() or user.username} (Profile: {profile_student_id})")
        else:
            missing_count += 1
            print(f"  ❌ {student_id} - ไม่พบในระบบ (username: {username})")
    
    # 3. สรุปผล
    print("\n\n" + "=" * 80)
    print("สรุปผลการตรวจสอบ")
    print("=" * 80)
    print(f"\nนักเรียนในระบบ: {found_count}/{len(expected_student_ids)} คน")
    print(f"นักเรียนที่หายไป: {missing_count} คน")
    
    if section:
        print(f"\nการลงทะเบียนในกลุ่มเรียน bis3r1:")
        print(f"  - ลงทะเบียนแล้ว: {enrolled_count} คน")
        print(f"  - ยังไม่ลงทะเบียน: {not_enrolled_count} คน")
        
        # ตรวจสอบข้อมูล Enrollment ทั้งหมดในกลุ่มเรียนนี้
        all_enrollments = Enrollment.objects.filter(section=section)
        print(f"\nข้อมูล Enrollment ทั้งหมดในกลุ่มเรียน bis3r1: {all_enrollments.count()} รายการ")
        
        if all_enrollments.exists():
            print("\nรายละเอียด Enrollment:")
            for idx, enrollment in enumerate(all_enrollments.select_related('student', 'section')[:10], 1):
                student = enrollment.student
                print(f"  {idx}. {student.username} - {student.get_full_name() or student.username}")
                print(f"     Section: {enrollment.section}")
                print(f"     Status: {enrollment.get_status_display()}")
                print(f"     Enrolled at: {enrollment.enrolled_at}")
    
    # 4. ตรวจสอบความสัมพันธ์
    print("\n\n4. ตรวจสอบความสัมพันธ์ข้อมูล")
    print("-" * 80)
    
    if section:
        # ตรวจสอบว่า Enrollment มี section ที่ถูกต้องหรือไม่
        enrollments_with_wrong_section = Enrollment.objects.filter(
            student__username__startswith='6834211',
            section__course__course_code='123456789'
        ).exclude(section=section)
        
        if enrollments_with_wrong_section.exists():
            print(f"⚠ พบนักเรียนที่ลงทะเบียนในกลุ่มเรียนอื่นของรายวิชา 123456789:")
            for enrollment in enrollments_with_wrong_section[:5]:
                print(f"  - {enrollment.student.username} - กลุ่ม {enrollment.section.section_number}")
        else:
            print("✓ ไม่พบปัญหาความสัมพันธ์")
    
    print("\n" + "=" * 80)
    print("เสร็จสมบูรณ์!")
    print("=" * 80)

if __name__ == '__main__':
    check_enrollments()

