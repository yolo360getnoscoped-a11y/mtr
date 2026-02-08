"""
Views for teacher dashboard
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from academic.models import Section


def is_teacher(user):
    """Check if user is teacher"""
    return user.is_authenticated and user.is_teacher()


@login_required
@user_passes_test(is_teacher)
def dashboard_view(request):
    """
    Teacher dashboard - หน้าหลักสำหรับอาจารย์
    """
    sections = Section.objects.filter(teacher=request.user).select_related('course', 'semester')
    
    context = {
        'sections': sections,
    }
    return render(request, 'teacher/dashboard.html', context)

