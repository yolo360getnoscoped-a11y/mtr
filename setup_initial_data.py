#!/usr/bin/env python
"""
Script to create initial data for the system
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from accounts.models import User, TeacherProfile, StudentProfile
from academic.models import AcademicYear, Semester, Course, Section, Enrollment

print("=" * 60)
print("กำลังสร้างข้อมูลเริ่มต้น...")
print("=" * 60)

# 1. สร้างปีการศึกษา (Academic Year)
print("\n1. สร้างปีการศึกษา...")
academic_year, created = AcademicYear.objects.get_or_create(
    year='2567',
    defaults={
        'description': 'ปีการศึกษา 2567',
        'is_active': True
    }
)
if created:
    print(f"   [OK] สร้างปีการศึกษา: {academic_year.year}")
else:
    print(f"   [EXISTS] พบปีการศึกษา: {academic_year.year} อยู่แล้ว")

# 2. สร้างภาคเรียน (Semester)
print("\n2. สร้างภาคเรียน...")
semester1, created = Semester.objects.get_or_create(
    academic_year=academic_year,
    semester_number=1,
    defaults={
        'start_date': date(2024, 6, 1),
        'end_date': date(2024, 9, 30),
        'is_active': True
    }
)
if created:
    print(f"   [OK] สร้างภาคเรียนที่ 1: {semester1}")
else:
    print(f"   [EXISTS] พบภาคเรียน: {semester1} อยู่แล้ว")

semester2, created = Semester.objects.get_or_create(
    academic_year=academic_year,
    semester_number=2,
    defaults={
        'start_date': date(2024, 11, 1),
        'end_date': date(2025, 2, 28),
        'is_active': True
    }
)
if created:
    print(f"   [OK] สร้างภาคเรียนที่ 2: {semester2}")
else:
    print(f"   [EXISTS] พบภาคเรียน: {semester2} อยู่แล้ว")

# 3. สร้างรายวิชา (Course)
print("\n3. สร้างรายวิชา...")
courses_data = [
    {'code': 'CS101', 'name': 'Introduction to Computer Science', 'credit': 3},
    {'code': 'CS201', 'name': 'Data Structures and Algorithms', 'credit': 3},
    {'code': 'CS301', 'name': 'Database Systems', 'credit': 3},
    {'code': 'CS302', 'name': 'Web Development', 'credit': 3},
]

for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        course_code=course_data['code'],
        defaults={
            'course_name': course_data['name'],
            'credit': course_data['credit'],
            'is_active': True
        }
    )
    if created:
        print(f"   [OK] สร้างรายวิชา: {course.course_code} - {course.course_name}")
    else:
        print(f"   [EXISTS] พบรายวิชา: {course.course_code} อยู่แล้ว")

# 4. สร้างบัญชีอาจารย์
print("\n4. สร้างบัญชีอาจารย์...")
teachers_data = [
    {'username': 'teacher1', 'email': 'teacher1@example.com', 'first_name': 'อาจารย์', 'last_name': 'สมชาย', 'employee_id': 'T001'},
    {'username': 'teacher2', 'email': 'teacher2@example.com', 'first_name': 'อาจารย์', 'last_name': 'สมหญิง', 'employee_id': 'T002'},
]

for teacher_data in teachers_data:
    teacher, created = User.objects.get_or_create(
        username=teacher_data['username'],
        defaults={
            'email': teacher_data['email'],
            'first_name': teacher_data['first_name'],
            'last_name': teacher_data['last_name'],
            'role': 'teacher',
            'is_staff': False
        }
    )
    if created:
        teacher.set_password('teacher123')
        teacher.save()
        TeacherProfile.objects.get_or_create(
            user=teacher,
            defaults={'employee_id': teacher_data['employee_id'], 'department': 'Computer Science'}
        )
        print(f"   [OK] สร้างอาจารย์: {teacher.username} (รหัส: {teacher_data['employee_id']}) - Password: teacher123")
    else:
        print(f"   [EXISTS] พบอาจารย์: {teacher.username} อยู่แล้ว")

# 5. สร้างบัญชีนักศึกษา
print("\n5. สร้างบัญชีนักศึกษา...")
students_data = [
    {'username': 'student1', 'email': 'student1@example.com', 'first_name': 'นักศึกษา', 'last_name': 'หนึ่ง', 'student_id': 'S001', 'year': 1},
    {'username': 'student2', 'email': 'student2@example.com', 'first_name': 'นักศึกษา', 'last_name': 'สอง', 'student_id': 'S002', 'year': 1},
    {'username': 'student3', 'email': 'student3@example.com', 'first_name': 'นักศึกษา', 'last_name': 'สาม', 'student_id': 'S003', 'year': 2},
    {'username': 'student4', 'email': 'student4@example.com', 'first_name': 'นักศึกษา', 'last_name': 'สี่', 'student_id': 'S004', 'year': 2},
    {'username': 'student5', 'email': 'student5@example.com', 'first_name': 'นักศึกษา', 'last_name': 'ห้า', 'student_id': 'S005', 'year': 3},
]

for student_data in students_data:
    student, created = User.objects.get_or_create(
        username=student_data['username'],
        defaults={
            'email': student_data['email'],
            'first_name': student_data['first_name'],
            'last_name': student_data['last_name'],
            'role': 'student',
            'is_staff': False
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        StudentProfile.objects.get_or_create(
            user=student,
            defaults={
                'student_id': student_data['student_id'],
                'year': student_data['year'],
                'major': 'Computer Science'
            }
        )
        print(f"   [OK] สร้างนักศึกษา: {student.username} (รหัส: {student_data['student_id']}) - Password: student123")
    else:
        print(f"   [EXISTS] พบนักศึกษา: {student.username} อยู่แล้ว")

# 6. สร้างกลุ่มเรียน (Section)
print("\n6. สร้างกลุ่มเรียน...")
teacher1 = User.objects.get(username='teacher1')
teacher2 = User.objects.get(username='teacher2')

sections_data = [
    {'course': 'CS101', 'semester': semester1, 'section': '1', 'teacher': teacher1, 'capacity': 30, 'room': 'LAB-101'},
    {'course': 'CS201', 'semester': semester1, 'section': '1', 'teacher': teacher1, 'capacity': 25, 'room': 'LAB-201'},
    {'course': 'CS301', 'semester': semester1, 'section': '1', 'teacher': teacher2, 'capacity': 20, 'room': 'LAB-301'},
    {'course': 'CS302', 'semester': semester1, 'section': '1', 'teacher': teacher2, 'capacity': 20, 'room': 'LAB-302'},
]

for section_data in sections_data:
    course = Course.objects.get(course_code=section_data['course'])
    section, created = Section.objects.get_or_create(
        course=course,
        semester=section_data['semester'],
        section_number=section_data['section'],
        defaults={
            'teacher': section_data['teacher'],
            'capacity': section_data['capacity'],
            'room': section_data['room']
        }
    )
    if created:
        print(f"   [OK] สร้างกลุ่มเรียน: {section}")
    else:
        print(f"   [EXISTS] พบกลุ่มเรียน: {section} อยู่แล้ว")

# 7. ลงทะเบียนนักศึกษาเข้ากลุ่มเรียน
print("\n7. ลงทะเบียนนักศึกษาเข้ากลุ่มเรียน...")
section1 = Section.objects.filter(course__course_code='CS101', section_number='1').first()
section2 = Section.objects.filter(course__course_code='CS201', section_number='1').first()

# ลงทะเบียนนักศึกษา 5 คนเข้า CS101
students = User.objects.filter(role='student')[:5]
for student in students:
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        section=section1,
        defaults={'status': 'enrolled'}
    )
    if created:
        print(f"   [OK] ลงทะเบียน {student.username} เข้า {section1}")

# ลงทะเบียนนักศึกษา 3 คนแรกเข้า CS201
for student in students[:3]:
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        section=section2,
        defaults={'status': 'enrolled'}
    )
    if created:
        print(f"   [OK] ลงทะเบียน {student.username} เข้า {section2}")

print("\n" + "=" * 60)
print("[SUCCESS] สร้างข้อมูลเริ่มต้นเสร็จสมบูรณ์!")
print("=" * 60)
print("\nสรุปข้อมูลที่สร้าง:")
print(f"   - ปีการศึกษา: {academic_year.year}")
print(f"   - ภาคเรียน: {semester1}, {semester2}")
print(f"   - รายวิชา: {Course.objects.count()} วิชา")
print(f"   - กลุ่มเรียน: {Section.objects.count()} กลุ่ม")
print(f"   - อาจารย์: {User.objects.filter(role='teacher').count()} คน")
print(f"   - นักศึกษา: {User.objects.filter(role='student').count()} คน")
print(f"   - การลงทะเบียน: {Enrollment.objects.count()} รายการ")
print("\nข้อมูลการเข้าสู่ระบบ:")
print("   Admin:")
print("     - Username: admin")
print("     - Password: admin123")
print("\n   Teacher:")
print("     - Username: teacher1, Password: teacher123")
print("     - Username: teacher2, Password: teacher123")
print("\n   Student:")
print("     - Username: student1-5, Password: student123")
print("=" * 60)

