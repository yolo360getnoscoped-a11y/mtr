#!/usr/bin/env python
"""
Script to add students to section bis3r1
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, UserProfile
from academic.models import Section, Enrollment, Course, Semester, AcademicYear

def add_students_to_bis3r1():
    """Add students to section bis3r1"""
    print("=" * 60)
    print("กำลังเพิ่มนักเรียนเข้าในกลุ่มเรียน bis3r1")
    print("=" * 60)
    
    # 1. ค้นหากลุ่มเรียน bis3r1
    section = None
    # ลองค้นหาด้วย section_number ที่ตรงกัน (case insensitive)
    sections = Section.objects.filter(section_number__iexact='bis3r1')
    if sections.exists():
        section = sections.first()
        print(f"\n✓ พบกลุ่มเรียน: {section}")
        print(f"   รายวิชา: {section.course.course_code} - {section.course.course_name}")
        print(f"   ภาคเรียน: {section.semester}")
        if section.teacher:
            print(f"   อาจารย์: {section.teacher.get_full_name() or section.teacher.username}")
        else:
            print(f"   อาจารย์: ยังไม่กำหนด")
    else:
        print("\n❌ ไม่พบกลุ่มเรียน bis3r1")
        print("\nกลุ่มเรียนที่มีในระบบ:")
        all_sections = Section.objects.all()[:20]  # แสดง 20 กลุ่มแรก
        for s in all_sections:
            print(f"  - {s.course.course_code} - กลุ่ม {s.section_number} (ID: {s.id})")
        return
    
    # 2. ตรวจสอบนักเรียนที่มีอยู่
    existing_students = User.objects.filter(role='student')
    print(f"\n✓ พบนักเรียนในระบบ: {existing_students.count()} คน")
    
    # 3. สร้างข้อมูลนักเรียนตัวอย่าง (ถ้ายังไม่มี)
    if existing_students.count() < 10:
        print("\nกำลังสร้างข้อมูลนักเรียนตัวอย่าง...")
        students_data = [
            {'username': 'std001', 'student_id': '68342110001-1', 'first_name': 'สมชาย', 'last_name': 'ใจดี'},
            {'username': 'std002', 'student_id': '68342110002-2', 'first_name': 'สมหญิง', 'last_name': 'รักเรียน'},
            {'username': 'std003', 'student_id': '68342110003-3', 'first_name': 'วิชัย', 'last_name': 'เก่งมาก'},
            {'username': 'std004', 'student_id': '68342110004-4', 'first_name': 'มานี', 'last_name': 'ขยันเรียน'},
            {'username': 'std005', 'student_id': '68342110005-5', 'first_name': 'ประเสริฐ', 'last_name': 'ดีงาม'},
            {'username': 'std006', 'student_id': '68342110006-6', 'first_name': 'สุดา', 'last_name': 'เรียนดี'},
            {'username': 'std007', 'student_id': '68342110007-7', 'first_name': 'ธีรพงษ์', 'last_name': 'มานะ'},
            {'username': 'std008', 'student_id': '68342110008-8', 'first_name': 'กาญจนา', 'last_name': 'ตั้งใจ'},
            {'username': 'std009', 'student_id': '68342110009-9', 'first_name': 'วรวิทย์', 'last_name': 'ขยัน'},
            {'username': 'std010', 'student_id': '68342110010-0', 'first_name': 'สุภาพ', 'last_name': 'ดีใจ'},
        ]
        
        created_count = 0
        for student_data in students_data:
            student, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'role': 'student',
                    'is_staff': False
                }
            )
            if created:
                student.set_password('changeme123')
                student.save()
                
                # Create profile
                profile, _ = UserProfile.objects.get_or_create(
                    user=student,
                    defaults={
                        'student_id': student_data['student_id']
                    }
                )
                created_count += 1
                print(f"   ✓ สร้างนักเรียน: {student.username} ({student.get_full_name()})")
        
        if created_count > 0:
            print(f"\n✓ สร้างนักเรียนใหม่ {created_count} คน")
    
    # 4. เพิ่มนักเรียนเข้าในกลุ่มเรียน bis3r1
    print(f"\n{'=' * 60}")
    print("4. เพิ่มนักเรียนเข้าในกลุ่มเรียน bis3r1...")
    print("=" * 60)
    
    # ดึงนักเรียนทั้งหมด (หรือเฉพาะที่ยังไม่ได้ลงทะเบียน)
    all_students = User.objects.filter(role='student')
    enrolled_students = Enrollment.objects.filter(section=section).values_list('student_id', flat=True)
    available_students = all_students.exclude(id__in=enrolled_students)
    
    print(f"   นักเรียนที่สามารถเพิ่มได้: {available_students.count()} คน")
    print(f"   นักเรียนที่ลงทะเบียนแล้ว: {len(enrolled_students)} คน")
    
    if available_students.count() == 0:
        print("\n   ⚠ นักเรียนทั้งหมดลงทะเบียนในกลุ่มเรียนนี้แล้ว")
        return
    
    # เพิ่มนักเรียน 10-15 คนแรก (หรือทั้งหมดถ้าน้อยกว่า 15)
    students_to_add = available_students[:15]
    added_count = 0
    skipped_count = 0
    
    for student in students_to_add:
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            section=section,
            defaults={'status': 'enrolled'}
        )
        if created:
            added_count += 1
            print(f"   ✓ เพิ่ม {student.get_full_name() or student.username} (รหัส: {student.profile.student_id if hasattr(student, 'profile') and student.profile.student_id else 'N/A'})")
        else:
            skipped_count += 1
    
    print(f"\n{'=' * 60}")
    print("✅ เสร็จสมบูรณ์!")
    print("=" * 60)
    print(f"\nสรุป:")
    print(f"  - กลุ่มเรียน: {section.course.course_code} - กลุ่ม {section.section_number}")
    print(f"  - เพิ่มนักเรียน: {added_count} คน")
    if skipped_count > 0:
        print(f"  - ข้าม (ลงทะเบียนแล้ว): {skipped_count} คน")
    print(f"  - รวมนักเรียนในกลุ่มเรียน: {Enrollment.objects.filter(section=section, status='enrolled').count()} คน")
    print(f"\nตอนนี้สามารถไปที่หน้า /academic/sections/ และเลือกรายวิชา/กลุ่มเรียนเพื่อดูข้อมูลนักเรียนได้แล้ว!")

if __name__ == '__main__':
    add_students_to_bis3r1()

