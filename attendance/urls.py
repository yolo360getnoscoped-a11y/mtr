"""
URL configuration for attendance app
"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('create-qr/<int:section_id>/', views.create_qr_session, name='create_qr'),
    path('qr-display/<int:session_id>/', views.qr_display, name='qr_display'),
    path('scan/', views.scan_page, name='scan_page'),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('scan-success/<int:record_id>/', views.scan_success, name='scan_success'),
    path('scan-expired/<int:record_id>/', views.scan_expired, name='scan_expired'),
    path('upload-proof/<int:record_id>/', views.upload_proof, name='upload_proof'),
    path('mark-status/<int:session_id>/', views.mark_attendance_status, name='mark_status'),
    path('report/', views.attendance_report, name='report'),
    path('student-detail/<int:section_id>/<int:student_id>/', views.student_attendance_detail, name='student_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('leave-approval/', views.leave_approval_list, name='leave_approval_list'),
    path('leave-approval/<int:leave_id>/', views.leave_approval_detail, name='leave_approval_detail'),
    path('report-summary/', views.report_summary, name='report_summary'),
    # Student views
    path('student/notifications/', views.student_notifications_view, name='student_notifications'),
    path('student/leave-request/', views.student_leave_request_list, name='student_leave_request_list'),
    path('student/leave-request/create/', views.student_leave_request_create, name='student_leave_request_create'),
    path('api/get-sections-by-date/', views.get_sections_by_date, name='get_sections_by_date'),
]

