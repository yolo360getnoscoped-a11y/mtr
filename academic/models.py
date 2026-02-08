"""
Models for academic app (D4, D5, D6, D7 - Academic Data Management)
"""
from django.db import models
from django.conf import settings


class AcademicYear(models.Model):
    """
    Academic Year (D4) - ปีการศึกษา
    """
    year = models.CharField(max_length=20, unique=True, verbose_name='ปีการศึกษา')
    description = models.TextField(blank=True, null=True, verbose_name='รายละเอียด')
    is_active = models.BooleanField(default=True, verbose_name='กำลังใช้งาน')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'ปีการศึกษา'
        verbose_name_plural = 'ปีการศึกษา'
        ordering = ['-year']
    
    def __str__(self):
        return self.year


class Semester(models.Model):
    """
    Semester (D5) - ภาคเรียน
    """
    SEMESTER_CHOICES = [
        (1, 'ภาคเรียนที่ 1'),
        (2, 'ภาคเรียนที่ 2'),
        (3, 'ภาคฤดูร้อน'),
    ]
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='semesters',
        verbose_name='ปีการศึกษา'
    )
    semester_number = models.IntegerField(choices=SEMESTER_CHOICES, verbose_name='ภาคเรียน')
    start_date = models.DateField(verbose_name='วันที่เริ่ม')
    end_date = models.DateField(verbose_name='วันที่สิ้นสุด')
    is_active = models.BooleanField(default=True, verbose_name='กำลังใช้งาน')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'ภาคเรียน'
        verbose_name_plural = 'ภาคเรียน'
        ordering = ['-academic_year', 'semester_number']
        unique_together = [['academic_year', 'semester_number']]
    
    def __str__(self):
        return f"{self.academic_year.year} - {self.get_semester_number_display()}"


class Course(models.Model):
    """
    Course (D6) - รายวิชา
    """
    course_code = models.CharField(max_length=20, unique=True, verbose_name='รหัสวิชา')
    course_name = models.CharField(max_length=200, verbose_name='ชื่อวิชา')
    credit = models.IntegerField(verbose_name='หน่วยกิต')
    description = models.TextField(blank=True, null=True, verbose_name='รายละเอียด')
    is_active = models.BooleanField(default=True, verbose_name='กำลังใช้งาน')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'รายวิชา'
        verbose_name_plural = 'รายวิชา'
        ordering = ['course_code']
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Section(models.Model):
    """
    Section (D7) - กลุ่มเรียน
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='รายวิชา'
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='ภาคเรียน'
    )
    section_number = models.CharField(max_length=10, verbose_name='เลขที่กลุ่ม')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_sections',
        limit_choices_to={'role': 'teacher'},
        verbose_name='อาจารย์ผู้สอน'
    )
    capacity = models.IntegerField(default=30, verbose_name='จำนวนรับ')
    room = models.CharField(max_length=50, blank=True, null=True, verbose_name='ห้องเรียน')
    schedule = models.CharField(max_length=200, blank=True, null=True, verbose_name='ตารางเรียน')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัพเดท')
    
    class Meta:
        verbose_name = 'กลุ่มเรียน'
        verbose_name_plural = 'กลุ่มเรียน'
        ordering = ['semester', 'course', 'section_number']
        unique_together = [['course', 'semester', 'section_number']]
    
    def __str__(self):
        return f"{self.course.course_code} - กลุ่ม {self.section_number} ({self.semester})"
    
    @property
    def enrolled_count(self):
        """จำนวนนักศึกษาที่ลงทะเบียน"""
        return self.enrollments.count()


class Enrollment(models.Model):
    """
    Enrollment - การลงทะเบียน (P4: บันทึกข้อมูลผู้เรียน)
    จับคู่ Student กับ Section
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
        verbose_name='นักศึกษา'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='กลุ่มเรียน'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่ลงทะเบียน')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'รอลงทะเบียน'),
            ('enrolled', 'ลงทะเบียน'),
            ('withdrawn', 'ถอน'),
            ('completed', 'เรียนจบ'),
        ],
        default='pending',
        verbose_name='สถานะ'
    )
    
    class Meta:
        verbose_name = 'การลงทะเบียน'
        verbose_name_plural = 'การลงทะเบียน'
        unique_together = [['student', 'section']]
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.section}"

