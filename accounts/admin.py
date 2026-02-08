from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Faculty, Major


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('ข้อมูลเพิ่มเติม', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('ข้อมูลเพิ่มเติม', {'fields': ('role', 'phone')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_role', 'get_employee_id', 'get_student_id', 'get_department']
    search_fields = ['user__username', 'user__email', 'teacher_employee_id', 'student_id', 'teacher_department', 'admin_department']
    list_filter = ['user__role']
    
    def get_role(self, obj):
        return obj.user.get_role_display()
    get_role.short_description = 'บทบาท'
    
    def get_employee_id(self, obj):
        return obj.teacher_employee_id if obj.user.is_teacher() else '-'
    get_employee_id.short_description = 'รหัสอาจารย์'
    
    def get_student_id(self, obj):
        return obj.student_id if obj.user.is_student() else '-'
    get_student_id.short_description = 'รหัสนักศึกษา'
    
    def get_department(self, obj):
        if obj.user.is_admin():
            return obj.admin_department
        elif obj.user.is_teacher():
            return obj.teacher_department
        return '-'
    get_department.short_description = 'หน่วยงาน/ภาควิชา'


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['faculty_code', 'faculty_name', 'created_at']
    search_fields = ['faculty_code', 'faculty_name']
    ordering = ['faculty_code']


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['major_code', 'major_name', 'faculty', 'created_at']
    search_fields = ['major_code', 'major_name', 'faculty__faculty_name']
    list_filter = ['faculty']
    ordering = ['faculty', 'major_code']

