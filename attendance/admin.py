from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord, LeaveRequest


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['section', 'session_date', 'session_time', 'teacher', 'is_active', 'created_at']
    list_filter = ['session_date', 'is_active', 'section__semester']
    search_fields = ['section__course__course_code', 'section__course__course_name']
    raw_id_fields = ['section', 'teacher']
    readonly_fields = ['created_at']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'checked_in_at']
    list_filter = ['status', 'session__session_date', 'session__section']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'session__section__course__course_code']
    raw_id_fields = ['session', 'student']
    readonly_fields = ['checked_in_at']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'section', 'leave_type', 'leave_date', 'status', 'teacher', 'created_at']
    list_filter = ['status', 'leave_type', 'leave_date', 'created_at']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'section__course__course_code']
    raw_id_fields = ['student', 'section', 'teacher']
    readonly_fields = ['created_at', 'updated_at']

