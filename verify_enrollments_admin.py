#!/usr/bin/env python
"""
Quick script to verify enrollments are in database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkin_project.settings')
django.setup()

from academic.models import Section, Enrollment

# Find bis3r1 section
section = Section.objects.filter(
    section_number__iexact='bis3r1',
    course__course_code='123456789'
).first()

if section:
    print(f"Section: {section} (ID: {section.id})")
    enrollments = Enrollment.objects.filter(section=section)
    print(f"Total enrollments: {enrollments.count()}")
    print(f"Enrolled: {enrollments.filter(status='enrolled').count()}")
    
    for e in enrollments[:5]:
        print(f"  - {e.student.username} - {e.get_status_display()}")
else:
    print("Section not found")

