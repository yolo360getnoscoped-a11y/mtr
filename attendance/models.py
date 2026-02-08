"""
Models for attendance app
"""
from django.db import models
from django.utils import timezone as tz
from datetime import timedelta
from accounts.models import User
from academic.models import Section


class AttendanceSession(models.Model):
    """
    Data Store D9: Attendance Session
    Represents a QR code session for attendance checking
    """
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='attendance_sessions')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    session_date = models.DateField()
    session_time = models.TimeField()
    session_datetime = models.DateTimeField()
    duration_minutes = models.IntegerField(default=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-session_datetime']
    
    def __str__(self):
        return f"{self.section.course.course_name} - {self.session_datetime}"
    
    def is_expired(self):
        """Check if session is expired (QR code expires after 1 hour from creation)"""
        if not self.created_at:
            return True
        # QR code expires 1 hour after creation
        expiry = self.created_at + timedelta(hours=1)
        return tz.now() > expiry
    
    def is_session_time_expired(self):
        """Check if session time has passed (for attendance status calculation)"""
        if not self.session_datetime:
            return True
        expiry = self.session_datetime + timedelta(minutes=self.duration_minutes)
        return tz.now() > expiry
    
    def get_qr_code_data(self):
        """Generate QR code data"""
        return f"ATTENDANCE:{self.id}:{self.section.id}"
    
    def save(self, *args, **kwargs):
        # Combine date and time into datetime
        if self.session_date and self.session_time:
            from datetime import datetime
            naive_datetime = datetime.combine(self.session_date, self.session_time)
            # Make it timezone-aware
            self.session_datetime = tz.make_aware(naive_datetime)
        super().save(*args, **kwargs)


class AttendanceRecord(models.Model):
    """
    Data Store D10: Attendance Record
    Records individual student attendance
    """
    STATUS_CHOICES = [
        ('present', 'เข้าเรียน'),
        ('absent', 'ขาดเรียน'),
        ('late', 'มาสาย'),
        ('excused', 'มีเหตุผล'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    checked_in_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    proof_image = models.ImageField(upload_to='attendance_proofs/', blank=True, null=True, verbose_name='หลักฐานการเข้าเรียน')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['session', 'student']
        ordering = ['-checked_in_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.session} - {self.get_status_display()}"


class LeaveRequest(models.Model):
    """
    Model for student leave requests
    """
    LEAVE_TYPE_CHOICES = [
        ('sick', 'ลาป่วย'),
        ('personal', 'ลากิจ'),
        ('other', 'อื่นๆ'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'รออนุมัติ'),
        ('approved', 'อนุมัติ'),
        ('rejected', 'ไม่อนุมัติ'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='sick')
    leave_date = models.DateField()
    reason = models.TextField()
    supporting_document = models.FileField(upload_to='leave_documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leave_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.leave_date} - {self.get_status_display()}"
    
    def get_status_class(self):
        """Get CSS class for status"""
        if self.status == 'approved':
            return 'status-approved'
        elif self.status == 'rejected':
            return 'status-rejected'
        else:
            return 'status-pending'
