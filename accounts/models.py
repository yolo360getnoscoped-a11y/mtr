"""
Models for accounts app (D1, D2, D3 - User Management)
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Faculty(models.Model):
    """
    Faculty Model - คณะ
    """
    faculty_code = models.CharField(max_length=20, unique=True, verbose_name='รหัสคณะ')
    faculty_name = models.CharField(max_length=200, verbose_name='ชื่อคณะ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'คณะ'
        verbose_name_plural = 'คณะ'
        ordering = ['faculty_code']
    
    def __str__(self):
        return f"{self.faculty_code} - {self.faculty_name}"


class Major(models.Model):
    """
    Major Model - สาขา
    """
    major_code = models.CharField(max_length=20, unique=True, verbose_name='รหัสสาขา')
    major_name = models.CharField(max_length=200, verbose_name='ชื่อสาขา')
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='majors',
        verbose_name='คณะ'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'สาขา'
        verbose_name_plural = 'สาขา'
        ordering = ['faculty', 'major_code']
    
    def __str__(self):
        return f"{self.major_code} - {self.major_name} ({self.faculty.faculty_name})"


class User(AbstractUser):
    """
    Custom User model extending AbstractUser
    Supports Admin, Teacher, and Student roles
    """
    ROLE_CHOICES = [
        ('admin', 'ผู้ดูแลระบบ'),
        ('teacher', 'อาจารย์'),
        ('student', 'นักศึกษา'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='บทบาท'
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='เบอร์โทรศัพท์')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name='รูปโปรไฟล์')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'ผู้ใช้'
        verbose_name_plural = 'ผู้ใช้'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    # Profile access methods (backward compatibility)
    @property
    def admin_profile(self):
        """Backward compatibility for admin_profile"""
        if self.is_admin():
            profile, _ = UserProfile.objects.get_or_create(user=self)
            return profile
        return None
    
    @property
    def teacher_profile(self):
        """Backward compatibility for teacher_profile"""
        if self.is_teacher():
            profile, _ = UserProfile.objects.get_or_create(user=self)
            return profile
        return None
    
    @property
    def student_profile(self):
        """Backward compatibility for student_profile"""
        if self.is_student():
            profile, _ = UserProfile.objects.get_or_create(user=self)
            return profile
        return None


class UserProfile(models.Model):
    """
    Unified Profile Model - รวมโปรไฟล์ของ Admin, Teacher, และ Student ในตารางเดียว
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='ผู้ใช้'
    )
    
    # Fields สำหรับ Admin
    admin_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='หน่วยงาน (Admin)')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ (Admin)')
    
    # Fields สำหรับ Teacher
    teacher_employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='รหัสอาจารย์')
    teacher_faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
        verbose_name='คณะ'
    )
    teacher_university_email = models.EmailField(blank=True, null=True, verbose_name='อีเมลมหาวิทยาลัย (Teacher)')
    teacher_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='ภาควิชา')
    teacher_office = models.CharField(max_length=200, blank=True, null=True, verbose_name='ห้องทำงาน')
    
    # Fields สำหรับ Student
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='รหัสนักศึกษา')
    student_major = models.ForeignKey(
        Major,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name='สาขา'
    )
    student_university_email = models.EmailField(blank=True, null=True, verbose_name='อีเมลมหาวิทยาลัย (Student)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'โปรไฟล์ผู้ใช้'
        verbose_name_plural = 'โปรไฟล์ผู้ใช้'
    
    def __str__(self):
        return f"Profile: {self.user.username} ({self.user.get_role_display()})"
    
    # Helper properties เพื่อเข้าถึงข้อมูลตาม role (backward compatibility)
    @property
    def employee_id(self):
        """สำหรับ Teacher - backward compatibility"""
        return self.teacher_employee_id if self.user.is_teacher() else None
    
    @property
    def department(self):
        """Department ตาม role - backward compatibility"""
        if self.user.is_admin():
            return self.admin_department
        elif self.user.is_teacher():
            return self.teacher_department
        return None
    
    @property
    def notes(self):
        """Notes สำหรับ Admin - backward compatibility"""
        return self.admin_notes if self.user.is_admin() else None
    
    @property
    def faculty(self):
        """Faculty สำหรับ Teacher - backward compatibility"""
        if self.user.is_teacher():
            return self.teacher_faculty.faculty_name if self.teacher_faculty else None
        return None
    
    @property
    def university_email(self):
        """University email ตาม role - backward compatibility"""
        if self.user.is_teacher():
            return self.teacher_university_email
        elif self.user.is_student():
            return self.student_university_email
        return None
    
    @property
    def office(self):
        """Office สำหรับ Teacher - backward compatibility"""
        return self.teacher_office if self.user.is_teacher() else None
    
    @property
    def major(self):
        """Major สำหรับ Student - backward compatibility"""
        if self.user.is_student():
            return self.student_major.major_name if self.student_major else None
        return None


# Backward compatibility models (deprecated - will be removed after migration)
class AdminProfile(models.Model):
    """Deprecated - Use UserProfile instead"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        verbose_name='ผู้ใช้'
    )
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='หน่วยงาน')
    notes = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')
    
    class Meta:
        verbose_name = 'โปรไฟล์ผู้ดูแลระบบ (Deprecated)'
        verbose_name_plural = 'โปรไฟล์ผู้ดูแลระบบ (Deprecated)'
    
    def __str__(self):
        return f"Admin Profile: {self.user.username}"


class TeacherProfile(models.Model):
    """Deprecated - Use UserProfile instead"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name='ผู้ใช้'
    )
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='รหัสอาจารย์')
    faculty = models.CharField(max_length=100, blank=True, null=True, verbose_name='คณะ')
    university_email = models.EmailField(blank=True, null=True, verbose_name='อีเมลมหาวิทยาลัย')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='ภาควิชา')
    office = models.CharField(max_length=200, blank=True, null=True, verbose_name='ห้องทำงาน')
    
    class Meta:
        verbose_name = 'โปรไฟล์อาจารย์ (Deprecated)'
        verbose_name_plural = 'โปรไฟล์อาจารย์ (Deprecated)'
    
    def __str__(self):
        return f"Teacher Profile: {self.user.get_full_name() or self.user.username}"


class StudentProfile(models.Model):
    """Deprecated - Use UserProfile instead"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='ผู้ใช้'
    )
    student_id = models.CharField(max_length=50, unique=True, verbose_name='รหัสนักศึกษา')
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name='สาขา')
    university_email = models.EmailField(blank=True, null=True, verbose_name='อีเมลมหาวิทยาลัย')
    
    class Meta:
        verbose_name = 'โปรไฟล์นักศึกษา (Deprecated)'
        verbose_name_plural = 'โปรไฟล์นักศึกษา (Deprecated)'
    
    def __str__(self):
        return f"Student Profile: {self.student_id} - {self.user.get_full_name() or self.user.username}"

