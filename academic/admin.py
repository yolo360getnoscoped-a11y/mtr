from django.contrib import admin
from .models import AcademicYear, Semester, Course, Section, Enrollment


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['year', 'description']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'semester_number', 'start_date', 'end_date', 'is_active']
    list_filter = ['academic_year', 'semester_number', 'is_active']
    search_fields = ['academic_year__year']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'course_name', 'credit', 'is_active']
    list_filter = ['is_active']
    search_fields = ['course_code', 'course_name']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['course', 'section_number', 'semester', 'teacher', 'capacity', 'enrolled_count', 'view_enrollments_link']
    list_filter = ['semester', 'course', 'teacher']
    search_fields = ['course__course_code', 'course__course_name', 'section_number']
    raw_id_fields = ['teacher']
    
    def enrolled_count(self, obj):
        return obj.enrolled_count
    enrolled_count.short_description = 'จำนวนที่ลงทะเบียน'
    enrolled_count.admin_order_field = 'enrollments__count'
    
    def view_enrollments_link(self, obj):
        """ลิงก์ไปดูรายละเอียดกลุ่มเรียน"""
        from django.utils.html import format_html
        from django.urls import reverse
        count = obj.enrollments.filter(status='enrolled').count()
        # ลิงก์ไปยังหน้า view section detail
        url = reverse('academic:section_detail', args=[obj.id])
        section_name = f"{obj.course.course_code} - กลุ่ม {obj.section_number}"
        return format_html(
            '<a href="{}" class="button" style="background: #417690; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block; margin: 2px;" target="_blank">📋 ดูกลุ่มเรียน<br><small style="font-size: 0.85em;">{}<br>👥 {} คน</small></a>',
            url,
            section_name,
            count
        )
    view_enrollments_link.short_description = 'ดูกลุ่มเรียน'
    view_enrollments_link.allow_tags = True


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'section_info', 'course_info', 'semester_info', 'teacher_info', 'status', 'enrolled_at']
    list_filter = ['status', 'section__semester', 'section__course', 'section__teacher', 'section__section_number']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'section__course__course_code', 'section__section_number']
    raw_id_fields = ['student', 'section']
    list_per_page = 50
    date_hierarchy = 'enrolled_at'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('student', 'section', 'section__course', 'section__semester', 'section__semester__academic_year', 'section__teacher')
    
    def section_info(self, obj):
        """แสดงข้อมูลกลุ่มเรียน"""
        if obj.section:
            return f"{obj.section.section_number}"
        return "-"
    section_info.short_description = 'กลุ่มเรียน'
    section_info.admin_order_field = 'section__section_number'
    
    def course_info(self, obj):
        """แสดงข้อมูลรายวิชา"""
        if obj.section and obj.section.course:
            return f"{obj.section.course.course_code} - {obj.section.course.course_name}"
        return "-"
    course_info.short_description = 'รายวิชา'
    course_info.admin_order_field = 'section__course__course_code'
    
    def semester_info(self, obj):
        """แสดงข้อมูลภาคเรียน"""
        if obj.section and obj.section.semester:
            semester = obj.section.semester
            year = semester.academic_year.year if semester.academic_year else "N/A"
            semester_num = semester.get_semester_number_display()
            return f"{year} - {semester_num}"
        return "-"
    semester_info.short_description = 'ปีการศึกษา / ภาคเรียน'
    semester_info.admin_order_field = 'section__semester'
    
    def teacher_info(self, obj):
        """แสดงข้อมูลอาจารย์ผู้สอน"""
        if obj.section and obj.section.teacher:
            teacher = obj.section.teacher
            return teacher.get_full_name() or teacher.username
        return "ยังไม่กำหนด"
    teacher_info.short_description = 'อาจารย์ผู้สอน'
    teacher_info.admin_order_field = 'section__teacher'

