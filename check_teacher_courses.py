#!/usr/bin/env python
"""
Script to check teacher courses and sections in database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User
from academic.models import Section, Course, Semester, AcademicYear, Enrollment

def check_teacher_courses():
    """Check teacher courses and sections"""
    print("=" * 80)
    print("ตรวจสอบข้อมูลอาจารย์ รายวิชา และกลุ่มเรียน")
    print("=" * 80)
    
    # 1. ตรวจสอบอาจารย์ ID=2
    print("\n1. ตรวจสอบอาจารย์ ID=2")
    print("-" * 80)
    
    teacher = User.objects.filter(id=2, role='teacher').first()
    if not teacher:
        print("❌ ไม่พบอาจารย์ ID=2")
        print("\nอาจารย์ที่มีในระบบ:")
        teachers = User.objects.filter(role='teacher')[:10]
        for t in teachers:
            print(f"  - ID: {t.id}, Username: {t.username}, Name: {t.get_full_name() or 'N/A'}")
    else:
        print(f"✓ พบอาจารย์: {teacher.username} ({teacher.get_full_name() or 'N/A'})")
        
        # 2. ตรวจสอบกลุ่มเรียนที่อาจารย์สอน
        print(f"\n2. ตรวจสอบกลุ่มเรียนที่อาจารย์ ID={teacher.id} สอน")
        print("-" * 80)
        
        sections = Section.objects.filter(teacher=teacher).select_related('course', 'semester', 'semester__academic_year')
        print(f"จำนวนกลุ่มเรียนทั้งหมด: {sections.count()} กลุ่ม")
        
        if sections.exists():
            print("\nรายละเอียดกลุ่มเรียน:")
            for idx, section in enumerate(sections, 1):
                course = section.course
                semester = section.semester
                year = semester.academic_year.year if semester.academic_year else "N/A"
                print(f"  {idx}. {course.course_code} - กลุ่ม {section.section_number}")
                print(f"     รายวิชา: {course.course_name}")
                print(f"     ภาคเรียน: {year} - {semester.get_semester_number_display()}")
                print(f"     Section ID: {section.id}, Course ID: {course.id}")
                print(f"     Semester ID: {semester.id}, Academic Year ID: {semester.academic_year.id if semester.academic_year else 'N/A'}")
                print()
        else:
            print("⚠ ไม่พบกลุ่มเรียนที่อาจารย์สอน")
        
        # 3. ตรวจสอบรายวิชาที่อาจารย์สอน (จากกลุ่มเรียน)
        print(f"\n3. ตรวจสอบรายวิชาที่อาจารย์ ID={teacher.id} สอน")
        print("-" * 80)
        
        courses = Course.objects.filter(sections__teacher=teacher).distinct()
        print(f"จำนวนรายวิชา: {courses.count()} วิชา")
        
        if courses.exists():
            print("\nรายละเอียดรายวิชา:")
            for idx, course in enumerate(courses, 1):
                course_sections = Section.objects.filter(course=course, teacher=teacher)
                print(f"  {idx}. {course.course_code} - {course.course_name} (Course ID: {course.id})")
                print(f"     กลุ่มเรียน: {', '.join([s.section_number for s in course_sections])}")
                print()
        else:
            print("⚠ ไม่พบรายวิชาที่อาจารย์สอน")
    
    # 4. ตรวจสอบภาคเรียนที่เลือก (2568 - ภาคเรียนที่ 1)
    print("\n4. ตรวจสอบภาคเรียน 2568 - ภาคเรียนที่ 1")
    print("-" * 80)
    
    academic_year = AcademicYear.objects.filter(year='2568').first()
    if not academic_year:
        print("❌ ไม่พบปีการศึกษา 2568")
        print("\nปีการศึกษาที่มีในระบบ:")
        years = AcademicYear.objects.all()[:10]
        for y in years:
            print(f"  - ID: {y.id}, Year: {y.year}")
    else:
        print(f"✓ พบปีการศึกษา: {academic_year.year} (ID: {academic_year.id})")
        
        semester = Semester.objects.filter(
            academic_year=academic_year,
            semester_number=1
        ).first()
        
        if not semester:
            print("❌ ไม่พบภาคเรียนที่ 1 ในปีการศึกษา 2568")
        else:
            print(f"✓ พบภาคเรียน: {semester.get_semester_number_display()} (ID: {semester.id})")
            
            # ตรวจสอบกลุ่มเรียนในภาคเรียนนี้
            if teacher:
                sections_in_semester = Section.objects.filter(
                    teacher=teacher,
                    semester=semester
                ).select_related('course')
                
                print(f"\nกลุ่มเรียนที่อาจารย์สอนในภาคเรียนนี้: {sections_in_semester.count()} กลุ่ม")
                
                if sections_in_semester.exists():
                    print("\nรายละเอียด:")
                    for idx, section in enumerate(sections_in_semester, 1):
                        print(f"  {idx}. {section.course.course_code} - กลุ่ม {section.section_number}")
                        print(f"     Course ID: {section.course.id}")
                        print(f"     Section ID: {section.id}")
                        print()
                    
                    # ตรวจสอบ courses ที่ unique
                    unique_courses = Course.objects.filter(
                        sections__teacher=teacher,
                        sections__semester=semester
                    ).distinct()
                    
                    print(f"\nรายวิชาที่ unique: {unique_courses.count()} วิชา")
                    for course in unique_courses:
                        print(f"  - {course.course_code} - {course.course_name} (ID: {course.id})")
                else:
                    print("⚠ ไม่พบกลุ่มเรียนที่อาจารย์สอนในภาคเรียนนี้")
    
    # 5. ตรวจสอบ query ที่ใช้ใน view
    print("\n5. ตรวจสอบ Query ที่ใช้ใน view")
    print("-" * 80)
    
    if teacher and academic_year:
        semester_obj = Semester.objects.filter(
            academic_year=academic_year,
            semester_number=1
        ).first()
        
        if semester_obj:
            # Query แบบเดียวกับใน view
            sections_for_teacher = Section.objects.filter(
                semester=semester_obj,
                teacher_id=teacher.id
            ).select_related('course', 'teacher')
            
            print(f"Query: Section.objects.filter(semester={semester_obj.id}, teacher_id={teacher.id})")
            print(f"ผลลัพธ์: {sections_for_teacher.count()} กลุ่มเรียน")
            
            if sections_for_teacher.exists():
                course_ids = sections_for_teacher.values_list('course_id', flat=True).distinct()
                print(f"Course IDs: {list(course_ids)}")
                
                courses_from_sections = Course.objects.filter(id__in=list(course_ids))
                print(f"Courses จาก query: {courses_from_sections.count()} วิชา")
                
                for course in courses_from_sections:
                    print(f"  - {course.course_code} - {course.course_name} (ID: {course.id})")
            else:
                print("⚠ Query ไม่พบข้อมูล")
    
    print("\n" + "=" * 80)
    print("เสร็จสมบูรณ์!")
    print("=" * 80)

if __name__ == '__main__':
    check_teacher_courses()

