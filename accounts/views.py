"""
Views for accounts app (P1 - Authentication)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import User, UserProfile
from django.db import connection


def home_view(request):
    """
    Home page - redirect based on authentication status
    """
    if request.user.is_authenticated:
        # Redirect based on role
        if request.user.is_admin():
            return redirect('academic:course_list')
        elif request.user.is_teacher():
            return redirect('teacher:dashboard')
        else:
            return redirect('attendance:scan_page')
    else:
        return redirect('accounts:login')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Process 1: ตรวจสอบสิทธิ์ (Login)
    """
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'ยินดีต้อนรับ {user.get_full_name() or user.username}')
                
                # Redirect based on role
                if user.is_admin():
                    return redirect('academic:course_list')
                elif user.is_teacher():
                    return redirect('teacher:dashboard')
                else:
                    return redirect('attendance:scan_page')
            else:
                messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
        else:
            messages.error(request, 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.info(request, 'คุณได้ออกจากระบบแล้ว')
    return redirect('accounts:login')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Register view - สมัครสมาชิก
    """
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        student_id = request.POST.get('student_id', '')
        # Set role to student automatically
        role = 'student'
        
        # Validation
        if not username or not email or not password1 or not password2:
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')
        elif not student_id:
            messages.error(request, 'กรุณากรอกรหัสนักศึกษา')
        elif password1 != password2:
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
        elif len(password1) < 8:
            messages.error(request, 'รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'อีเมลนี้ถูกใช้งานแล้ว')
        else:
            try:
                from academic.models import Enrollment
                
                # Check if student_id already exists
                existing_profile = UserProfile.objects.filter(student_id=student_id).first()
                
                if existing_profile and existing_profile.user:
                    # Check if this is the placeholder user created from Excel upload
                    # (username starts with "student_")
                    if existing_profile.user.username.startswith('student_'):
                        # This is a placeholder user from Excel upload
                        # We'll update it instead of creating new user
                        old_user = existing_profile.user
                        
                        # Update user information
                        old_user.username = username
                        old_user.email = email
                        old_user.set_password(password1)
                        old_user.first_name = first_name
                        old_user.last_name = last_name
                        old_user.save()
                        
                        # Update profile with major
                        major_id = request.POST.get('major_id')
                        if major_id:
                            from .models import Major
                            try:
                                major = Major.objects.get(id=major_id)
                                existing_profile.student_major = major
                                existing_profile.save()
                            except Major.DoesNotExist:
                                pass
                        
                        # Find and update pending enrollments
                        pending_enrollments = Enrollment.objects.filter(
                            student=old_user,
                            status='pending'
                        )
                        
                        if pending_enrollments.exists():
                            updated_count = pending_enrollments.update(status='enrolled')
                            messages.success(request, f'สมัครสมาชิกสำเร็จ! ระบบได้อัปเดตการลงทะเบียน {updated_count} รายการแล้ว กรุณาเข้าสู่ระบบ')
                        else:
                            messages.success(request, 'สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ')
                        
                        return redirect('accounts:login')
                    else:
                        # Real user already exists with this student_id
                        messages.error(request, 'รหัสนักศึกษานี้ถูกใช้งานแล้ว')
                        # Get faculties and majors for rendering
                        faculties = []
                        majors = []
                        
                        try:
                            from .models import Faculty, Major
                            from django.db import ProgrammingError, OperationalError
                            
                            try:
                                faculties = list(Faculty.objects.all().order_by('faculty_code'))
                            except (ProgrammingError, OperationalError, Exception):
                                faculties = []
                            
                            try:
                                majors = list(Major.objects.all().order_by('faculty', 'major_code'))
                            except (ProgrammingError, OperationalError, Exception):
                                majors = []
                        except Exception:
                            pass
                        context = {
                            'faculties': faculties,
                            'majors': majors,
                        }
                        return render(request, 'accounts/register.html', context)
                
                # Create new user with student role
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )
                
                # Create student profile
                from .models import Faculty, Major
                profile = UserProfile.objects.create(
                    user=user,
                    student_id=student_id,
                )
                
                # Set major if provided
                major_id = request.POST.get('major_id')
                if major_id:
                    try:
                        major = Major.objects.get(id=major_id)
                        profile.student_major = major
                        profile.save()
                    except Major.DoesNotExist:
                        pass
                
                # Find and update pending enrollments with matching student_id
                # Look for enrollments where the student's profile has this student_id
                # These are enrollments created from Excel upload
                pending_enrollments = Enrollment.objects.filter(
                    student__profile__student_id=student_id,
                    status='pending'
                )
                
                if pending_enrollments.exists():
                    # Update enrollments: change student to new user and status to enrolled
                    updated_count = 0
                    for enrollment in pending_enrollments:
                        enrollment.student = user
                        enrollment.status = 'enrolled'
                        enrollment.save()
                        updated_count += 1
                    
                    messages.success(request, f'สมัครสมาชิกสำเร็จ! ระบบได้อัปเดตการลงทะเบียน {updated_count} รายการแล้ว กรุณาเข้าสู่ระบบ')
                else:
                    messages.success(request, 'สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ')
                
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    # Get faculties and majors for dropdown
    # Handle case where tables might not exist yet (migrations not run)
    faculties = []
    majors = []
    
    try:
        from .models import Faculty, Major
        from django.db import ProgrammingError, OperationalError
        
        # Try to get faculties
        try:
            faculties = list(Faculty.objects.all().order_by('faculty_code'))
        except (ProgrammingError, OperationalError):
            faculties = []
        except Exception:
            faculties = []
        
        # Try to get majors
        try:
            majors = list(Major.objects.all().order_by('faculty', 'major_code'))
        except (ProgrammingError, OperationalError):
            majors = []
        except Exception:
            majors = []
    except Exception:
        # If import fails or any other error
        faculties = []
        majors = []
    
    context = {
        'faculties': faculties,
        'majors': majors,
    }
    return render(request, 'accounts/register.html', context)


@login_required
def profile_view(request):
    """
    User profile view
    """
    user = request.user
    context = {
        'user': user,
    }
    
    # Get user profile (unified)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    context['profile'] = profile
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """
    Edit profile view
    """
    user = request.user
    
    if request.method == 'POST':
        # Update user basic info
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        # Update profile (unified)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if user.is_teacher():
            profile.teacher_employee_id = request.POST.get('employee_id', profile.teacher_employee_id)
            # Update faculty
            faculty_id = request.POST.get('faculty_id')
            if faculty_id:
                from .models import Faculty
                try:
                    faculty = Faculty.objects.get(id=faculty_id)
                    profile.teacher_faculty = faculty
                except Faculty.DoesNotExist:
                    pass
            elif faculty_id == '':
                # Clear faculty if empty
                profile.teacher_faculty = None
            # Update major (for teacher, using student_major field as "สาขา")
            major_id = request.POST.get('major_id')
            if major_id:
                from .models import Major
                try:
                    major = Major.objects.get(id=major_id)
                    profile.student_major = major
                except Major.DoesNotExist:
                    pass
            elif major_id == '':
                # Clear major if empty
                profile.student_major = None
        elif user.is_student():
            # Update faculty (via major)
            faculty_id = request.POST.get('faculty_id')
            major_id = request.POST.get('major_id')
            if major_id:
                from .models import Major
                try:
                    major = Major.objects.get(id=major_id)
                    profile.student_major = major
                except Major.DoesNotExist:
                    pass
            elif major_id == '':
                # Clear major if empty
                profile.student_major = None
        elif user.is_admin():
            profile.admin_department = request.POST.get('department', profile.admin_department)
        profile.save()
        
        messages.success(request, 'แก้ไขโปรไฟล์สำเร็จ')
        return redirect('accounts:profile')
    
    # Get profile data
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Get faculties and majors for dropdown
    faculties = []
    majors = []
    
    try:
        from .models import Faculty, Major
        from django.db import ProgrammingError, OperationalError
        
        try:
            faculties = list(Faculty.objects.all().order_by('faculty_code'))
        except (ProgrammingError, OperationalError, Exception):
            faculties = []
        
        try:
            majors = list(Major.objects.all().order_by('faculty', 'major_code'))
        except (ProgrammingError, OperationalError, Exception):
            majors = []
    except Exception:
        pass
    
    context = {
        'user': user,
        'profile': profile,
        'faculties': faculties,
        'majors': majors,
    }
    
    return render(request, 'accounts/edit_profile.html', context)


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_admin()


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """
    หน้าจัดการผู้ใช้สำหรับ Admin
    """
    # Get filter parameters
    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('search', '')
    
    # Start with all users
    users = User.objects.all()
    
    # Filter by role
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Search by username, email, first_name, last_name
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Order by username
    users = users.order_by('username')
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@user_passes_test(is_admin)
def user_add(request):
    """
    เพิ่มผู้ใช้ใหม่ (Admin only)
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'student')
        phone = request.POST.get('phone', '')
        
        # Role-specific fields
        student_id = request.POST.get('student_id', '')
        employee_id = request.POST.get('employee_id', '')
        department = request.POST.get('department', '')
        major = request.POST.get('major', '')
        university_email = request.POST.get('university_email', '')
        section_id = request.POST.get('section_id', '')
        faculty = request.POST.get('faculty', '')
        teacher_university_email = request.POST.get('teacher_university_email', '')
        teacher_course_id = request.POST.get('teacher_course_id', '')
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'อีเมลนี้ถูกใช้งานแล้ว')
        elif role == 'student' and not student_id:
            messages.error(request, 'กรุณากรอกรหัสนักศึกษา')
        elif role == 'student' and UserProfile.objects.filter(student_id=student_id).exists():
            messages.error(request, 'รหัสนักศึกษานี้ถูกใช้งานแล้ว')
        elif role == 'teacher' and employee_id and UserProfile.objects.filter(teacher_employee_id=employee_id).exists():
            messages.error(request, 'รหัสอาจารย์นี้ถูกใช้งานแล้ว')
        else:
            try:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    phone=phone if phone else None
                )
                
                # Create profile (unified)
                profile = UserProfile.objects.create(user=user)
                if role == 'student':
                    profile.student_id = student_id
                    profile.student_major = major
                    profile.student_university_email = university_email if university_email else None
                    profile.save()
                    
                    # Create enrollment if section is provided
                    if section_id:
                        from academic.models import Section, Enrollment
                        try:
                            section = Section.objects.get(id=section_id)
                            Enrollment.objects.create(
                                student=user,
                                section=section,
                                status='enrolled'
                            )
                        except Section.DoesNotExist:
                            pass
                elif role == 'teacher':
                    profile.teacher_employee_id = employee_id if employee_id else None
                    profile.teacher_faculty = faculty if faculty else None
                    profile.teacher_university_email = teacher_university_email if teacher_university_email else None
                    profile.teacher_department = department
                    profile.teacher_office = request.POST.get('office', '')
                    profile.save()
                    
                    # Assign teacher to section if course is provided
                    if teacher_course_id:
                        from academic.models import Section, Course
                        try:
                            course = Course.objects.get(id=teacher_course_id)
                            # Get or create a section for this course and assign teacher
                            from datetime import datetime
                            from academic.models import AcademicYear, Semester
                            
                            # Get or create current academic year
                            current_year = datetime.now().year + 543  # Thai Buddhist year
                            academic_year, _ = AcademicYear.objects.get_or_create(
                                year=current_year,
                                defaults={'description': f'ปีการศึกษา {current_year}'}
                            )
                            
                            # Get or create current semester (default to semester 1)
                            semester, _ = Semester.objects.get_or_create(
                                academic_year=academic_year,
                                semester_number=1,
                                defaults={
                                    'start_date': datetime.now().date(),
                                    'end_date': datetime.now().date(),
                                    'is_active': True
                                }
                            )
                            
                            # Get or create section for this teacher
                            section, created = Section.objects.get_or_create(
                                course=course,
                                semester=semester,
                                section_number='1',
                                defaults={
                                    'teacher': user,
                                    'capacity': 30
                                }
                            )
                            if not created:
                                section.teacher = user
                                section.save()
                        except (Course.DoesNotExist, Exception):
                            pass
                elif role == 'admin':
                    profile.admin_department = department
                    profile.admin_notes = request.POST.get('notes', '')
                    profile.save()
                
                messages.success(request, f'เพิ่มผู้ใช้ {username} สำเร็จ')
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    # Get all sections for dropdown
    from academic.models import Section, Course
    sections = Section.objects.select_related('course', 'semester').all().order_by('course__course_code', 'section_number')
    courses = Course.objects.filter(is_active=True).order_by('course_code')
    
    context = {
        'sections': sections,
        'courses': courses,
        'edit_user': None,  # ไม่มี user object สำหรับหน้า add
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """
    แก้ไขผู้ใช้ (Admin only)
    """
    user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from editing themselves (optional safety check)
    # if user == request.user:
    #     messages.warning(request, 'คุณไม่สามารถแก้ไขข้อมูลของตัวเองได้')
    #     return redirect('accounts:user_list')
    
    if request.method == 'POST':
        # Update user basic info
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.role = request.POST.get('role', user.role)
        
        # Handle password change
        new_password = request.POST.get('password', '')
        if new_password:
            user.set_password(new_password)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        # Update or create profile (unified)
        profile, created = UserProfile.objects.get_or_create(user=user)
        if user.role == 'student':
            profile.student_id = request.POST.get('student_id', profile.student_id or '')
            profile.student_major = request.POST.get('major', profile.student_major or '')
            profile.student_university_email = request.POST.get('university_email', profile.student_university_email or '')
            profile.save()
            
            # Update enrollment if section is provided
            section_id = request.POST.get('section_id', '')
            if section_id:
                from academic.models import Section, Enrollment
                try:
                    section = Section.objects.get(id=section_id)
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=user,
                        section=section,
                        defaults={'status': 'enrolled'}
                    )
                    if not created:
                        enrollment.status = 'enrolled'
                        enrollment.save()
                except Section.DoesNotExist:
                    pass
        elif user.role == 'teacher':
            profile.teacher_employee_id = request.POST.get('employee_id', profile.teacher_employee_id or '')
            profile.teacher_faculty = request.POST.get('faculty', profile.teacher_faculty or '')
            profile.teacher_university_email = request.POST.get('teacher_university_email', profile.teacher_university_email or '')
            profile.teacher_department = request.POST.get('department', profile.teacher_department or '')
            profile.teacher_office = request.POST.get('office', profile.teacher_office or '')
            profile.save()
            
            # Update section assignment if course is provided
            teacher_course_id = request.POST.get('teacher_course_id', '')
            if teacher_course_id:
                from academic.models import Section, Course
                try:
                    course = Course.objects.get(id=teacher_course_id)
                    # Get first active section for this course or create one
                    from datetime import datetime
                    from academic.models import AcademicYear, Semester
                    
                    # Get or create current academic year
                    current_year = datetime.now().year + 543  # Thai Buddhist year
                    academic_year, _ = AcademicYear.objects.get_or_create(
                        year=current_year,
                        defaults={'description': f'ปีการศึกษา {current_year}'}
                    )
                    
                    # Get or create current semester (default to semester 1)
                    semester, _ = Semester.objects.get_or_create(
                        academic_year=academic_year,
                        semester_number=1,
                        defaults={
                            'start_date': datetime.now().date(),
                            'end_date': datetime.now().date(),
                            'is_active': True
                        }
                    )
                    
                    # Get first section for this course or create one
                    section = Section.objects.filter(course=course, semester=semester).first()
                    if not section:
                        section = Section.objects.create(
                            course=course,
                            semester=semester,
                            section_number='1',
                            teacher=user,
                            capacity=30
                        )
                    else:
                        section.teacher = user
                        section.save()
                except (Course.DoesNotExist, Exception):
                    pass
        elif user.role == 'admin':
            profile.admin_department = request.POST.get('department', profile.admin_department or '')
            profile.admin_notes = request.POST.get('notes', profile.admin_notes or '')
            profile.save()
        
        messages.success(request, f'แก้ไขผู้ใช้ {user.username} สำเร็จ')
        return redirect('accounts:user_list')
    
    # Get all sections for dropdown
    from academic.models import Section, Course
    sections = Section.objects.select_related('course', 'semester').all().order_by('course__course_code', 'section_number')
    courses = Course.objects.filter(is_active=True).order_by('course_code')
    
    # Get profile data
    context = {
        'edit_user': user,  # ใช้ edit_user เพื่อแยกจาก request.user
        'sections': sections,
        'courses': courses,
    }
    
    profile, _ = UserProfile.objects.get_or_create(user=user)
    context['profile'] = profile
    
    return render(request, 'accounts/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    """
    ลบผู้ใช้ (Admin only)
    """
    user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deleting themselves
    if user == request.user:
        messages.error(request, 'คุณไม่สามารถลบบัญชีของตัวเองได้')
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'ลบผู้ใช้ {username} สำเร็จ')
        return redirect('accounts:user_list')
    
    context = {
        'user': user,
    }
    return render(request, 'accounts/user_delete.html', context)


@login_required
@user_passes_test(is_admin)
def batch_delete_users(request):
    """
    ลบผู้ใช้หลายคนพร้อมกัน (Admin only)
    """
    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids')
        
        if not user_ids:
            messages.error(request, 'กรุณาเลือกผู้ใช้ที่ต้องการลบ')
            return redirect('accounts:user_list')
        
        deleted_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                
                # Prevent admin from deleting themselves
                if user == request.user:
                    failed_count += 1
                    continue
                
                username = user.username
                user.delete()
                deleted_count += 1
            except User.DoesNotExist:
                failed_count += 1
            except Exception as e:
                failed_count += 1
        
        if deleted_count > 0:
            messages.success(request, f'ลบผู้ใช้ {deleted_count} รายการสำเร็จ')
        if failed_count > 0:
            messages.warning(request, f'ไม่สามารถลบผู้ใช้ {failed_count} รายการ')
        
        return redirect('accounts:user_list')
    
    return redirect('accounts:user_list')

# ใน Python shell นี้ รันสั่งนี้:
tables = connection.introspection.table_names()
for table in tables:
    print(table)

# ดู Users
from accounts.models import User
User.objects.all().values('username', 'role', 'email')

# ดู Courses
from academic.models import Course
Course.objects.all().values('course_code', 'course_name')

# ดู Sections
from academic.models import Section
Section.objects.all().values('section_number', 'course_id', 'teacher_id')

# ดู Enrollments
from academic.models import Enrollment
Enrollment.objects.all().values('student_id', 'section_id', 'status')

