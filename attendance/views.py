"""
Views for attendance app (P5, P6, P7, P8 - Attendance Management)
"""
import json
import qrcode
from io import BytesIO
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from .models import AttendanceSession, AttendanceRecord, LeaveRequest
from academic.models import Section
from accounts.models import User


def is_teacher(user):
    """Check if user is teacher"""
    return user.is_authenticated and user.is_teacher()


def is_student(user):
    """Check if user is student"""
    return user.is_authenticated and user.is_student()


@login_required
@user_passes_test(is_teacher)
def create_qr_session(request, section_id):
    """
    Process 5: สร้าง QR Code
    อาจารย์สร้างเซสชันเช็คชื่อและ QR Code
    """
    section = get_object_or_404(Section, id=section_id, teacher=request.user)
    
    if request.method == 'POST':
        session_date_str = request.POST.get('session_date')
        session_time_str = request.POST.get('session_time')
        duration_minutes = int(request.POST.get('duration_minutes', 15))
        
        if session_date_str and session_time_str:
            try:
                from datetime import datetime
                # Parse date string to date object
                session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
                # Parse time string to time object
                session_time = datetime.strptime(session_time_str, '%H:%M').time()
                
                # Limit QR code duration to maximum 1 hour (60 minutes)
                if duration_minutes > 60:
                    duration_minutes = 60
                    messages.warning(request, 'ระยะเวลาถูกจำกัดไม่เกิน 1 ชั่วโมง')
                
                session = AttendanceSession.objects.create(
                    section=section,
                    teacher=request.user,
                    session_date=session_date,
                    session_time=session_time,
                    duration_minutes=duration_minutes
                )
                messages.success(request, 'สร้าง QR Code สำเร็จ')
                return redirect('attendance:qr_display', session_id=session.id)
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
        else:
            messages.error(request, 'กรุณากรอกวันที่และเวลา')
    
    context = {
        'section': section,
    }
    return render(request, 'attendance/create_qr.html', context)


@login_required
@user_passes_test(is_teacher)
def qr_display(request, session_id):
    """
    หน้าแสดง QR Code สำหรับอาจารย์ (แสดงบนโปรเจคเตอร์)
    """
    session = get_object_or_404(AttendanceSession, id=session_id, teacher=request.user)
    
    # Generate QR Code
    qr_data = session.get_qr_code_data()
    qr_data_dict = {
        'session_id': session.id,
        'section_id': session.section.id,
        'data': qr_data
    }
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Get attendance statistics
    records = AttendanceRecord.objects.filter(session=session)
    total_students = session.section.enrolled_count
    present_count = records.filter(status='present').count()
    late_count = records.filter(status='late').count()
    absent_count = total_students - present_count - late_count
    
    context = {
        'session': session,
        'qr_image': img_str,
        'qr_data': qr_data_dict,
        'total_students': total_students,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'records': records,
    }
    return render(request, 'attendance/qr_display.html', context)


@login_required
@user_passes_test(is_student)
def scan_page(request):
    """
    หน้าสำหรับนักศึกษาสแกน QR Code
    """
    return render(request, 'attendance/scan_page.html')


@csrf_exempt
def scan_qr(request):
    """
    Process 6: บันทึกการเข้าเรียน
    API endpoint สำหรับการสแกน QR Code
    """
    # Manual auth checks so JSON API returns JSON errors instead of HTML redirects
    is_json_request = (request.content_type == 'application/json') or (request.headers.get('X-Requested-With') == 'XMLHttpRequest')

    if not request.user.is_authenticated:
        if is_json_request:
            return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        else:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(next=request.path)

    if not is_student(request.user):
        if is_json_request:
            return JsonResponse({'success': False, 'message': 'Forbidden'}, status=403)
        else:
            return JsonResponse({'success': False, 'message': 'Forbidden'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        # Handle both JSON and form-data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            qr_data = data.get('data') or data.get('token')
            session_id = data.get('session_id')
            proof_image = None
        else:
            # Form data (for file upload)
            qr_data = request.POST.get('data') or request.POST.get('token')
            session_id = request.POST.get('session_id')
            proof_image = request.FILES.get('proof_image')
        
        if not qr_data or not session_id:
            return JsonResponse({'success': False, 'message': 'ข้อมูลไม่ครบถ้วน'}, status=400)
        
        # Find session
        session = AttendanceSession.objects.filter(
            id=session_id,
            is_active=True
        ).first()
        
        # Verify QR code data
        if not session:
            return JsonResponse({'success': False, 'message': 'QR Code ไม่ถูกต้องหรือหมดอายุ'}, status=404)
        
        if session.get_qr_code_data() != qr_data:
            return JsonResponse({'success': False, 'message': 'QR Code ไม่ถูกต้อง'}, status=404)
        
        # Check if QR code expired (1 hour from creation time)
        # If expired, reject scanning and mark as absent without creating record
        is_qr_expired = session.is_expired()
        
        if is_qr_expired:
            # QR code expired - cannot scan, mark as absent
            # Check if student is enrolled first
            from academic.models import Enrollment
            enrollment = Enrollment.objects.filter(
                student=request.user,
                section=session.section,
                status='enrolled'
            ).first()
            
            if not enrollment:
                return JsonResponse({'success': False, 'message': 'คุณไม่ได้ลงทะเบียนในกลุ่มเรียนนี้'}, status=403)
            
            # Check if already has a record
            existing_record = AttendanceRecord.objects.filter(
                session=session,
                student=request.user
            ).first()
            
            if existing_record:
                return JsonResponse({
                    'success': False,
                    'message': f'คุณเช็คชื่อแล้ว (สถานะ: {existing_record.get_status_display()})'
                }, status=400)
            
            # Create absent record for expired QR code
            record = AttendanceRecord.objects.create(
                session=session,
                student=request.user,
                status='absent',
                proof_image=proof_image
            )
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'QR Code หมดเวลา (ถ่ายรูปไว้แล้วสแกนย้อนหลังไม่ได้)',
                    'status': 'expired',
                    'record_id': record.id
                }, status=400)
            else:
                return redirect('attendance:scan_expired', record_id=record.id)
        
        # Check if student is enrolled in this section
        from academic.models import Enrollment
        enrollment = Enrollment.objects.filter(
            student=request.user,
            section=session.section,
            status='enrolled'
        ).first()
        
        if not enrollment:
            return JsonResponse({'success': False, 'message': 'คุณไม่ได้ลงทะเบียนในกลุ่มเรียนนี้'}, status=403)
        
        # Check if already scanned
        existing_record = AttendanceRecord.objects.filter(
            session=session,
            student=request.user
        ).first()
        
        if existing_record:
            return JsonResponse({
                'success': False,
                'message': f'คุณเช็คชื่อแล้ว (สถานะ: {existing_record.get_status_display()})'
            }, status=400)
        
        # Determine status (present, late, or absent) based on session time
        # Get session datetime
        if not session.session_datetime:
            # Fallback: combine date and time if session_datetime is not set
            session_datetime = timezone.datetime.combine(session.session_date, session.session_time)
            session_datetime = timezone.make_aware(session_datetime)
        else:
            session_datetime = session.session_datetime
        
        current_time = timezone.now()
        late_threshold = session_datetime + timedelta(minutes=15)  # 15 minutes
        absent_threshold = session_datetime + timedelta(hours=1)  # 1 hour
        
        # Determine status based on time (QR code is still valid, check session time)
        if current_time > absent_threshold:
            # If scanned after 1 hour from session time, mark as absent
            status = 'absent'
        elif current_time > late_threshold:
            # If scanned after 15 minutes but before 1 hour, mark as late
            status = 'late'
        else:
            # If scanned within 15 minutes, mark as present
            status = 'present'
        
        # Create attendance record
        record = AttendanceRecord.objects.create(
            session=session,
            student=request.user,
            status=status,
            proof_image=proof_image
        )
        
        # If request is JSON, return JSON response
        if request.content_type == 'application/json':
            message = f'เช็คชื่อสำเร็จ (สถานะ: {record.get_status_display()})'
            return JsonResponse({
                'success': True,
                'message': message,
                'status': record.status,
                'record_id': record.id,
                'redirect_url': f'/attendance/scan-success/{record.id}/'
            })
        else:
            # Form submission - redirect to success page
            from django.shortcuts import redirect
            return redirect('attendance:scan_success', record_id=record.id)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'ข้อมูลไม่ถูกต้อง'}, status=400)
    except Exception as e:
        if request.content_type == 'application/json':
            return JsonResponse({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}, status=500)
        else:
            from django.contrib import messages
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
            return redirect('attendance:scan_page')


@login_required
@user_passes_test(is_student)
def scan_expired(request, record_id):
    """
    หน้าแสดงข้อความ QR Code หมดเวลา
    """
    record = get_object_or_404(AttendanceRecord, id=record_id, student=request.user)
    session = record.session
    
    # Get student ID
    student_id = "-"
    if hasattr(request.user, 'student_profile') and request.user.student_profile:
        student_id = request.user.student_profile.student_id
    elif hasattr(request.user, 'student_id'):
        student_id = request.user.student_id
    
    context = {
        'record': record,
        'session': session,
        'student_id': student_id,
    }
    return render(request, 'attendance/scan_expired.html', context)


@login_required
@user_passes_test(is_student)
def scan_success(request, record_id):
    """
    หน้าแสดงผลการเช็คชื่อสำเร็จ
    """
    record = get_object_or_404(AttendanceRecord, id=record_id, student=request.user)
    session = record.session
    
    # Get student ID
    student_id = "-"
    if hasattr(request.user, 'student_profile') and request.user.student_profile:
        student_id = request.user.student_profile.student_id
    elif hasattr(request.user, 'student_id'):
        student_id = request.user.student_id
    
    # Format check-in time
    check_time = record.checked_in_at
    if not check_time:
        check_time = timezone.now()
    
    context = {
        'record': record,
        'session': session,
        'student_id': student_id,
        'check_time': check_time,
        'status_display': record.get_status_display(),
    }
    return render(request, 'attendance/scan_success.html', context)


@login_required
@user_passes_test(is_student)
def upload_proof(request, record_id):
    """
    อัพเดทหลักฐานการเข้าเรียนหลังจากสแกนแล้ว
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    record = get_object_or_404(AttendanceRecord, id=record_id, student=request.user)
    
    if 'proof_image' in request.FILES:
        record.proof_image = request.FILES['proof_image']
        record.save()
        return JsonResponse({'success': True, 'message': 'อัพโหลดหลักฐานสำเร็จ'})
    else:
        return JsonResponse({'success': False, 'message': 'ไม่พบไฟล์'}, status=400)


@login_required
@user_passes_test(is_teacher)
def mark_attendance_status(request, session_id):
    """
    Process 7: บันทึกสถานะการเข้าเรียน
    อาจารย์แก้ไขสถานะการเข้าเรียนของนักศึกษา
    """
    session = get_object_or_404(AttendanceSession, id=session_id, teacher=request.user)
    
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if record_id and new_status:
            record = get_object_or_404(AttendanceRecord, id=record_id, session=session)
            record.status = new_status
            record.updated_by = request.user
            record.notes = notes
            record.save()
            messages.success(request, 'แก้ไขสถานะสำเร็จ')
        else:
            messages.error(request, 'ข้อมูลไม่ครบถ้วน')
        
        return redirect('attendance:mark_status', session_id=session_id)
    
    records = AttendanceRecord.objects.filter(session=session).select_related('student')
    context = {
        'session': session,
        'records': records,
    }
    return render(request, 'attendance/mark_status.html', context)


@login_required
def attendance_report(request):
    """
    Process 8: รายงาน
    สร้างรายงานการเข้าเรียนตามเงื่อนไข
    """
    context = {}
    
    if request.user.is_admin():
        # Admin can see all reports
        sections = Section.objects.all()
    elif request.user.is_teacher():
        # Teacher can see their sections
        sections = Section.objects.filter(teacher=request.user)
    else:
        # Student can see their enrollments
        from academic.models import Enrollment
        sections = Section.objects.filter(enrollments__student=request.user).distinct()
    
    # Get filter parameters
    section_id = request.GET.get('section_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Convert "None" string to None
    if start_date == 'None' or start_date == '':
        start_date = None
    if end_date == 'None' or end_date == '':
        end_date = None
    
    if section_id:
        section = get_object_or_404(Section, id=section_id)
        sessions = AttendanceSession.objects.filter(section=section)
        
        if start_date:
            sessions = sessions.filter(session_date__gte=start_date)
        if end_date:
            sessions = sessions.filter(session_date__lte=end_date)
        
        # Calculate statistics
        total_sessions = sessions.count()
        records = AttendanceRecord.objects.filter(session__in=sessions)
        
        if request.user.is_student():
            # Student view: their own attendance
            records = records.filter(student=request.user)
            total_attended = records.count()
            present_count = records.filter(status='present').count()
            late_count = records.filter(status='late').count()
            absent_count = total_sessions - total_attended
            
            context.update({
                'section': section,
                'total_sessions': total_sessions,
                'total_attended': total_attended,
                'present_count': present_count,
                'late_count': late_count,
                'absent_count': absent_count,
                'attendance_rate': (total_attended / total_sessions * 100) if total_sessions > 0 else 0,
                'records': records.order_by('-session__session_date', '-session__session_time'),
            })
        else:
            # Admin/Teacher view: all students
            from academic.models import Enrollment
            enrolled_students = Enrollment.objects.filter(section=section, status='enrolled').values_list('student_id', flat=True)
            
            student_stats = []
            for student_id in enrolled_students:
                student = request.user.__class__.objects.get(id=student_id)
                student_records = records.filter(student=student)
                student_stats.append({
                    'student': student,
                    'total_attended': student_records.count(),
                    'present_count': student_records.filter(status='present').count(),
                    'late_count': student_records.filter(status='late').count(),
                    'absent_count': total_sessions - student_records.count(),
                    'attendance_rate': (student_records.count() / total_sessions * 100) if total_sessions > 0 else 0,
                })
            
            # Calculate summary statistics for chart
            total_enrolled = len(enrolled_students)
            students_attended = len([s for s in student_stats if s['total_attended'] > 0])
            students_absent = len([s for s in student_stats if s['absent_count'] > 0 and s['total_attended'] == 0])
            # Count students with leave requests that are approved
            from .models import LeaveRequest
            leave_filter = LeaveRequest.objects.filter(
                section=section,
                status='approved'
            )
            if start_date:
                leave_filter = leave_filter.filter(leave_date__gte=start_date)
            if end_date:
                leave_filter = leave_filter.filter(leave_date__lte=end_date)
            approved_leaves = leave_filter.values_list('student_id', flat=True).distinct().count()
            
            context.update({
                'section': section,
                'total_sessions': total_sessions,
                'student_stats': student_stats,
                'sessions': sessions.order_by('-session_date', '-session_time'),
                'summary_stats': {
                    'total_enrolled': total_enrolled,
                    'students_attended': students_attended,
                    'students_absent': students_absent,
                    'students_on_leave': approved_leaves,
                }
            })
    
    context.update({
        'sections': sections,
        'selected_section': section_id,
        'start_date': start_date,
        'end_date': end_date,
    })
    
    return render(request, 'attendance/report.html', context)


@login_required
@user_passes_test(lambda u: u.is_teacher() or u.is_admin())
def student_attendance_detail(request, section_id, student_id):
    """
    หน้ารายละเอียดการเข้าเรียนของนักศึกษาแต่ละคน
    """
    section = get_object_or_404(Section, id=section_id)
    student = get_object_or_404(User, id=student_id)
    
    # Check permissions
    if request.user.is_teacher() and section.teacher != request.user:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('attendance:report')
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Convert "None" string to None
    if start_date == 'None' or start_date == '':
        start_date = None
    if end_date == 'None' or end_date == '':
        end_date = None
    
    # Get sessions for this section
    sessions = AttendanceSession.objects.filter(section=section)
    
    if start_date:
        sessions = sessions.filter(session_date__gte=start_date)
    if end_date:
        sessions = sessions.filter(session_date__lte=end_date)
    
    # Get attendance records for this student
    records = AttendanceRecord.objects.filter(
        session__in=sessions,
        student=student
    ).select_related('session').order_by('-session__session_date', '-session__session_time')
    
    # Get all sessions to calculate absent count
    all_sessions = sessions.order_by('-session_date', '-session_time')
    
    # Create a list of tuples with (session, record) for easier template access
    session_records = []
    records_dict = {record.session.id: record for record in records}
    for session in all_sessions:
        record = records_dict.get(session.id)
        session_records.append((session, record))
    
    # Calculate statistics
    total_sessions = all_sessions.count()
    total_attended = records.count()
    present_count = records.filter(status='present').count()
    late_count = records.filter(status='late').count()
    absent_count = total_sessions - total_attended
    
    # Get student ID
    student_id_display = "-"
    if hasattr(student, 'student_profile') and student.student_profile:
        student_id_display = student.student_profile.student_id
    
    context = {
        'section': section,
        'student': student,
        'student_id': student_id_display,
        'records': records,
        'session_records': session_records,
        'all_sessions': all_sessions,
        'total_sessions': total_sessions,
        'total_attended': total_attended,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'attendance_rate': (total_attended / total_sessions * 100) if total_sessions > 0 else 0,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'attendance/student_detail.html', context)


@login_required
def report_summary(request):
    """
    หน้าสรุปรายงานการเข้าเรียน
    """
    context = {}
    
    if request.user.is_admin():
        sections = Section.objects.all()
    elif request.user.is_teacher():
        sections = Section.objects.filter(teacher=request.user)
    else:
        from academic.models import Enrollment
        sections = Section.objects.filter(enrollments__student=request.user).distinct()
    
    # Get filter parameters
    section_id = request.GET.get('section_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Convert "None" string to None
    if start_date == 'None' or start_date == '':
        start_date = None
    if end_date == 'None' or end_date == '':
        end_date = None
    
    if section_id:
        section = get_object_or_404(Section, id=section_id)
        sessions = AttendanceSession.objects.filter(section=section)
        
        if start_date:
            sessions = sessions.filter(session_date__gte=start_date)
        if end_date:
            sessions = sessions.filter(session_date__lte=end_date)
        
        # Calculate statistics
        total_sessions = sessions.count()
        records = AttendanceRecord.objects.filter(session__in=sessions)
        
        if not request.user.is_student():
            # Admin/Teacher view: summary statistics
            from academic.models import Enrollment
            enrolled_students = Enrollment.objects.filter(section=section, status='enrolled').values_list('student_id', flat=True)
            
            # Calculate summary statistics for chart
            total_enrolled = len(enrolled_students)
            student_stats = []
            for student_id in enrolled_students:
                student = request.user.__class__.objects.get(id=student_id)
                student_records = records.filter(student=student)
                student_stats.append({
                    'student': student,
                    'total_attended': student_records.count(),
                    'present_count': student_records.filter(status='present').count(),
                    'late_count': student_records.filter(status='late').count(),
                    'absent_count': total_sessions - student_records.count(),
                    'attendance_rate': (student_records.count() / total_sessions * 100) if total_sessions > 0 else 0,
                })
            
            students_attended = len([s for s in student_stats if s['total_attended'] > 0])
            students_absent = len([s for s in student_stats if s['absent_count'] > 0 and s['total_attended'] == 0])
            
            # Count students with leave requests that are approved
            from .models import LeaveRequest
            leave_filter = LeaveRequest.objects.filter(
                section=section,
                status='approved'
            )
            if start_date:
                leave_filter = leave_filter.filter(leave_date__gte=start_date)
            if end_date:
                leave_filter = leave_filter.filter(leave_date__lte=end_date)
            approved_leaves = leave_filter.values_list('student_id', flat=True).distinct().count()
            
            context.update({
                'section': section,
                'total_sessions': total_sessions,
                'summary_stats': {
                    'total_enrolled': total_enrolled,
                    'students_attended': students_attended,
                    'students_absent': students_absent,
                    'students_on_leave': approved_leaves,
                }
            })
    
    context.update({
        'sections': sections,
        'selected_section': section_id,
        'start_date': start_date,
        'end_date': end_date,
    })
    
    return render(request, 'attendance/report_summary.html', context)


@login_required
@user_passes_test(lambda u: u.is_teacher() or u.is_admin())
def notifications_view(request):
    """
    หน้าสำหรับ Teacher/Admin ดูการแจ้งเตือน (ดูได้อย่างเดียว)
    """
    # Get all sections - Admin sees all, Teacher sees only their sections
    if request.user.is_admin():
        sections = Section.objects.all()
        leave_requests = LeaveRequest.objects.all()
        recent_sessions = AttendanceSession.objects.all()
    else:
        sections = Section.objects.filter(teacher=request.user)
        leave_requests = LeaveRequest.objects.filter(section__in=sections)
        recent_sessions = AttendanceSession.objects.filter(section__in=sections)
    
    # Get all leave requests (for viewing only)
    leave_requests = leave_requests.select_related('student', 'section', 'section__course').order_by('-created_at')
    
    # Get recent attendance records that might need attention
    from datetime import datetime, timedelta
    recent_sessions = recent_sessions.filter(
        session_datetime__gte=timezone.now() - timedelta(days=7)
    ).order_by('-session_datetime')
    
    context = {
        'leave_requests': leave_requests,
        'recent_sessions': recent_sessions,
        'sections': sections,
    }
    return render(request, 'attendance/notifications.html', context)


@login_required
@user_passes_test(lambda u: u.is_teacher() or u.is_admin())
def leave_approval_list(request):
    """
    หน้าสำหรับ Teacher/Admin ดูรายการการแจ้งลาที่รออนุมัติ
    """
    # Get all sections - Admin sees all, Teacher sees only their sections
    if request.user.is_admin():
        sections = Section.objects.all()
        leave_requests = LeaveRequest.objects.all()
    else:
        sections = Section.objects.filter(teacher=request.user)
        leave_requests = LeaveRequest.objects.filter(section__in=sections)
    
    # Get leave requests
    leave_requests = leave_requests.select_related('student', 'section', 'section__course', 'teacher').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        leave_requests = leave_requests.filter(status=status_filter)
    
    # Filter by section if provided (for Admin)
    section_filter = request.GET.get('section_id')
    if section_filter and request.user.is_admin():
        leave_requests = leave_requests.filter(section_id=section_filter)
    
    context = {
        'leave_requests': leave_requests,
        'status_filter': status_filter,
        'sections': sections,
        'selected_section': section_filter,
    }
    return render(request, 'attendance/leave_approval_list.html', context)


@login_required
@user_passes_test(lambda u: u.is_teacher() or u.is_admin())
def leave_approval_detail(request, leave_id):
    """
    หน้าสำหรับ Teacher ดูรายละเอียดและอนุมัติ/ไม่อนุมัติการลา
    """
    # Admin can approve any leave request, Teacher can only approve their sections
    if request.user.is_admin():
        leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    else:
        leave_request = get_object_or_404(
            LeaveRequest, 
            id=leave_id,
            section__teacher=request.user
        )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            leave_request.status = 'approved'
            leave_request.teacher = request.user
            leave_request.reviewed_at = timezone.now()
            leave_request.save()
            messages.success(request, 'อนุมัติการลาสำเร็จ')
        elif action == 'reject':
            leave_request.status = 'rejected'
            leave_request.teacher = request.user
            leave_request.reviewed_at = timezone.now()
            leave_request.save()
            messages.success(request, 'ปฏิเสธการลาสำเร็จ')
        
        return redirect('attendance:leave_approval_list')
    
    context = {
        'leave_request': leave_request,
    }
    return render(request, 'attendance/leave_approval_detail.html', context)


@login_required
@user_passes_test(is_student)
def student_notifications_view(request):
    """
    หน้าสำหรับ Student ดูการแจ้งเตือน (สถานะ leave requests, upcoming sessions)
    """
    # Get student's enrolled sections
    from academic.models import Enrollment
    enrollments = Enrollment.objects.filter(student=request.user, status='enrolled')
    sections = [e.section for e in enrollments]
    
    # Get leave requests for this student
    leave_requests = LeaveRequest.objects.filter(
        student=request.user
    ).select_related('section', 'section__course').order_by('-created_at')[:10]
    
    # Get upcoming attendance sessions (next 7 days)
    upcoming_sessions = AttendanceSession.objects.filter(
        section__in=sections,
        session_datetime__gte=timezone.now(),
        session_datetime__lte=timezone.now() + timedelta(days=7)
    ).order_by('session_datetime')[:10]
    
    # Get recent attendance records
    try:
        recent_records = AttendanceRecord.objects.filter(
            student=request.user
        ).select_related('session', 'session__section', 'session__section__course').order_by('-checked_in_at')[:10]
    except Exception:
        # Fallback if checked_in_at field doesn't exist yet
        recent_records = AttendanceRecord.objects.filter(
            student=request.user
        ).select_related('session', 'session__section', 'session__section__course').order_by('-id')[:10]
    
    context = {
        'leave_requests': leave_requests,
        'upcoming_sessions': upcoming_sessions,
        'recent_records': recent_records,
    }
    return render(request, 'attendance/student_notifications.html', context)


@login_required
@user_passes_test(is_student)
def student_leave_request_list(request):
    """
    หน้าสำหรับ Student ดูรายการคำขอลาของตัวเอง
    """
    leave_requests = LeaveRequest.objects.filter(
        student=request.user
    ).select_related('section', 'section__course', 'teacher').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        leave_requests = leave_requests.filter(status=status_filter)
    
    context = {
        'leave_requests': leave_requests,
        'status_filter': status_filter,
    }
    return render(request, 'attendance/student_leave_request_list.html', context)


@login_required
@user_passes_test(is_student)
def student_leave_request_create(request):
    """
    หน้าสำหรับ Student สร้างคำขอลาใหม่
    """
    # Get all sections (student can select any section)
    from academic.models import Section
    sections = Section.objects.filter(course__is_active=True).select_related('course', 'teacher').order_by('course__course_code', 'section_number')
    
    if request.method == 'POST':
        section_id = request.POST.get('section')
        leave_type = request.POST.get('leave_type')
        leave_date = request.POST.get('leave_date')
        reason = request.POST.get('reason')
        supporting_document = request.FILES.get('supporting_document')
        
        if not all([section_id, leave_type, leave_date, reason]):
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')
        else:
            try:
                section = get_object_or_404(Section, id=section_id)
                
                # Get teacher from section
                teacher = section.teacher if section.teacher else None
                
                # Create leave request
                leave_request = LeaveRequest.objects.create(
                    student=request.user,
                    section=section,
                    leave_type=leave_type,
                    leave_date=leave_date,
                    reason=reason,
                    supporting_document=supporting_document,
                    status='pending',
                    teacher=teacher  # Set teacher from section
                )
                
                messages.success(request, 'ส่งคำขอลาสำเร็จ รออาจารย์อนุมัติ')
                return redirect('attendance:student_leave_request_list')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    context = {
        'sections': sections,
    }
    return render(request, 'attendance/student_leave_request_create.html', context)


@login_required
@user_passes_test(is_student)
def get_sections_by_date(request):
    """
    API endpoint สำหรับดึง sections ที่มี class ในวันที่เลือก
    """
    from datetime import datetime
    from academic.models import Enrollment
    
    leave_date_str = request.GET.get('leave_date')
    if not leave_date_str:
        return JsonResponse({'error': 'กรุณาระบุวันที่ลา'}, status=400)
    
    try:
        leave_date = datetime.strptime(leave_date_str, '%Y-%m-%d').date()
        weekday = leave_date.strftime('%A')  # Monday, Tuesday, etc.
        
        # Map weekday to Thai day names
        weekday_map = {
            'Monday': ['จันทร์', 'จ.'],
            'Tuesday': ['อังคาร', 'อ.'],
            'Wednesday': ['พุธ', 'พ.'],
            'Thursday': ['พฤหัสบดี', 'พฤ.'],
            'Friday': ['ศุกร์', 'ศ.'],
            'Saturday': ['เสาร์', 'ส.'],
            'Sunday': ['อาทิตย์', 'อา.']
        }
        
        day_names = weekday_map.get(weekday, [])
        
        # Get student's enrolled sections
        enrollments = Enrollment.objects.filter(student=request.user, status='enrolled')
        sections = [e.section for e in enrollments]
        
        # Filter sections that have schedule matching the day
        filtered_sections = []
        for section in sections:
            if section.schedule:
                # Check if schedule contains the day name
                schedule_lower = section.schedule.lower()
                for day_name in day_names:
                    if day_name.lower() in schedule_lower.lower():
                        filtered_sections.append({
                            'id': section.id,
                            'course_code': section.course.course_code,
                            'course_name': section.course.course_name,
                            'section_number': section.section_number,
                            'schedule': section.schedule,
                            'teacher_name': section.teacher.get_full_name() if section.teacher else 'ยังไม่กำหนดอาจารย์'
                        })
                        break
        
        return JsonResponse({
            'sections': filtered_sections,
            'date': leave_date_str,
            'weekday': weekday
        })
    except ValueError:
        return JsonResponse({'error': 'รูปแบบวันที่ไม่ถูกต้อง'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

