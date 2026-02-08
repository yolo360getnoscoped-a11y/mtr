#!/usr/bin/env python
"""
Script to fix and verify enrollment data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile
from academic.models import Section, Enrollment, Course

def fix_enrollments():
    """Fix and verify enrollment data"""
    print("=" * 80)
    print("ตรวจสอบและแก้ไขข้อมูลการลงทะเบียน")
    print("=" * 80)
    
    # 1. ค้นหากลุ่มเรียน bis3r1 (รายวิชา 123456789)
    section = Section.objects.filter(
        section_number__iexact='bis3r1',
        course__course_code='123456789'
    ).select_related('course', 'semester', 'teacher').first()
    
    if not section:
        print("❌ ไม่พบกลุ่มเรียน bis3r1 (รายวิชา 123456789)")
        return
    
    print(f"\n✓ พบกลุ่มเรียน: {section}")
    print(f"   รายวิชา: {section.course.course_code} - {section.course.course_name}")
    print(f"   ภาคเรียน: {section.semester}")
    print(f"   Section ID: {section.id}")
    
    # 2. ตรวจสอบ Enrollment ทั้งหมด
    all_enrollments = Enrollment.objects.filter(section=section)
    print(f"\nการลงทะเบียนทั้งหมด: {all_enrollments.count()} รายการ")
    
    enrolled = all_enrollments.filter(status='enrolled')
    print(f"  - ลงทะเบียน: {enrolled.count()} คน")
    
    # 3. ตรวจสอบนักเรียนที่ควรจะมี
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
    
    print(f"\nตรวจสอบ {len(expected_student_ids)} คน...")
    
    missing_enrollments = []
    found_enrollments = []
    
    for student_id in expected_student_ids:
        username = student_id.replace('-', '')
        user = User.objects.filter(username=username, role='student').first()
        
        if user:
            enrollment = Enrollment.objects.filter(
                student=user,
                section=section
            ).first()
            
            if enrollment:
                found_enrollments.append((student_id, user, enrollment))
                print(f"  ✓ {student_id} - {user.get_full_name() or user.username} (Enrollment ID: {enrollment.id})")
            else:
                missing_enrollments.append((student_id, user))
                print(f"  ❌ {student_id} - {user.get_full_name() or user.username} (ยังไม่ลงทะเบียน)")
        else:
            print(f"  ⚠ {student_id} - ไม่พบผู้ใช้ในระบบ")
    
    # 4. แสดงสรุป
    print("\n" + "=" * 80)
    print("สรุปผล")
    print("=" * 80)
    print(f"\nพบการลงทะเบียน: {len(found_enrollments)}/{len(expected_student_ids)} คน")
    print(f"ยังไม่ลงทะเบียน: {len(missing_enrollments)} คน")
    
    # 5. แสดงรายละเอียด Enrollment ที่พบ
    if found_enrollments:
        print(f"\nรายละเอียด Enrollment ที่พบ ({len(found_enrollments)} รายการ):")
        for student_id, user, enrollment in found_enrollments[:10]:
            print(f"  - Enrollment ID: {enrollment.id}")
            print(f"    Student: {user.username} ({user.get_full_name() or 'N/A'})")
            print(f"    Section: {enrollment.section} (ID: {enrollment.section.id})")
            print(f"    Status: {enrollment.get_status_display()}")
            print(f"    Enrolled at: {enrollment.enrolled_at}")
            print()
    
    # 6. ตรวจสอบข้อมูลในฐานข้อมูลโดยตรง
    print("\n" + "=" * 80)
    print("ตรวจสอบข้อมูลในฐานข้อมูล")
    print("=" * 80)
    
    from django.db import connection
    with connection.cursor() as cursor:
        # นับจำนวน Enrollment ในกลุ่มเรียนนี้
        cursor.execute("""
            SELECT COUNT(*) 
            FROM academic_enrollment 
            WHERE section_id = %s
        """, [section.id])
        count = cursor.fetchone()[0]
        print(f"\nจำนวน Enrollment ในฐานข้อมูล (section_id={section.id}): {count}")
        
        # แสดง Enrollment 10 รายการแรก
        cursor.execute("""
            SELECT e.id, e.student_id, e.section_id, e.status, e.enrolled_at,
                   u.username, u.first_name, u.last_name
            FROM academic_enrollment e
            JOIN accounts_user u ON e.student_id = u.id
            WHERE e.section_id = %s
            ORDER BY e.enrolled_at DESC
            LIMIT 10
        """, [section.id])
        
        rows = cursor.fetchall()
        if rows:
            print(f"\nEnrollment 10 รายการล่าสุด:")
            for row in rows:
                print(f"  - ID: {row[0]}, Student: {row[5]} ({row[6]} {row[7]}), Status: {row[3]}, Section ID: {row[2]}")
        else:
            print("\n⚠ ไม่พบข้อมูล Enrollment ในฐานข้อมูล")
    
    print("\n" + "=" * 80)
    print("เสร็จสมบูรณ์!")
    print("=" * 80)
    print("\nคำแนะนำ:")
    print("1. ตรวจสอบว่า Enrollment records ถูกสร้างในฐานข้อมูลหรือไม่")
    print("2. ตรวจสอบว่า section_id ถูกต้องหรือไม่")
    print("3. ลองรีเฟรชหน้า Django Admin")
    print("4. ตรวจสอบว่า Django Admin filter ไม่ได้กรองข้อมูลออก")

if __name__ == '__main__':
    fix_enrollments()

