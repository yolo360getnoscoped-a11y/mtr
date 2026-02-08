"""
URL configuration for academic app
"""
from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.manage_course, name='course_add'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/', views.manage_course, name='course_edit'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('courses/<int:course_id>/manage-teachers/', views.manage_course_teachers, name='manage_course_teachers'),
    path('courses/<int:course_id>/manage-students/', views.manage_course_students, name='manage_course_students'),
    path('sections/', views.section_list, name='section_list'),
    path('sections/add/', views.section_add, name='section_add'),
    path('sections/<int:section_id>/edit/', views.section_edit, name='section_edit'),
    path('sections/<int:section_id>/delete/', views.section_delete, name='section_delete'),
    path('sections/<int:section_id>/assign-teacher/', views.assign_teacher, name='assign_teacher'),
    path('my-sections/', views.my_sections, name='my_sections'),
    path('sections/<int:section_id>/enrollment/', views.manage_enrollment, name='manage_enrollment'),
    path('sections/<int:section_id>/', views.section_detail, name='section_detail'),
    path('sections/<int:section_id>/delete-enrollment/<int:enrollment_id>/', views.delete_enrollment, name='delete_enrollment'),
    path('sections/<int:section_id>/batch-delete-enrollments/', views.batch_delete_enrollments, name='batch_delete_enrollments'),
    # Import students from Excel
    path('import-students/', views.import_students_excel, name='import_students_excel'),
    path('api/get-sections-by-course/', views.get_sections_by_course, name='get_sections_by_course'),
    path('create-courses-for-teacher/', views.create_courses_for_teacher, name='create_courses_for_teacher'),
    path('add-students-to-bis3r1/', views.add_students_to_bis3r1, name='add_students_to_bis3r1'),
    path('add-students-to-bis3r2/', views.add_students_to_bis3r2, name='add_students_to_bis3r2'),
    path('add-students-from-list/', views.add_students_from_list, name='add_students_from_list'),
]

