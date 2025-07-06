from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import test_email

from .views import (
    home, about_view, contact_view,
    events_view, event_detail_view,
    register, login_view, student_dashboard,
    student_profile_view, my_courses,
    teacher_dashboard,
)
from django.contrib.auth import views as auth_views
#C:\Users\1030G3\Desktop\school project\.venv\Lib\site-packages\certifi\cacert.pem

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('events/', views.events_view, name='events'),
    path('events/<slug:slug>/', views.event_detail_view, name='event_detail'), 
    path('register/', views.register, name='register'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', student_profile_view, name='student_profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', views.login_view, name='login'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('upload_note/', views.upload_note, name='upload_note'),
    path('teacher_notes/', views.teacher_notes, name='teacher_notes'),
    path('student_notes/', views.student_notes, name='student_notes'),
    path('note/<int:note_id>/', views.view_note_detail, name='view_note_detail'),
    path('delete_note/<int:note_id>/', views.delete_note, name='delete_note'),
    path('clear_notes/', views.clear_all_notes, name='clear_notes'),
    path('my-assignments/', views.my_assignments, name='my_assignments'),
    path('create-assignment/', views.create_assignment, name='create_assignment'),
    path('assignments/', views.student_assignments, name='student_assignments'),
    path('assignment/<int:assignment_id>/', views.assignment_detail_student, name='assignment_detail_student'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    
    path('assignment/<int:assignment_id>/teacher/submissions/', views.teacher_view_submissions, name='teacher_view_submissions'),
    path('submission/<int:assignment_id>/delete/', views.delete_submission, name='delete_submission'),
    path('pay-fees/', views.pay_fees, name='pay_fees'),
    path('payment/verify/', views.verify_payment, name='payment_verify'),
    path('payment/receipt/', views.payment_receipt, name='payment_receipt'),
    path('payment/clear/', views.clear_payment_history, name='clear_payment_history'),
    path('profile', views.teacher_profile, name='teacher_profile'),
    path('leave/status/', views.leave_status, name='leave_status'),
    path('leave/request/', views.request_leave, name='request_leave'),
    path('admin/leave/requests/', views.admin_leave_list, name='admin_leave_list'),
    path('admin/leave/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
    path('admin/leave/<int:leave_id>/decline/', views.decline_leave, name='decline_leave'),
    path('grades/upload/', views.upload_grade, name='upload_grade'),
    path('student/result/', views.view_result, name='view_result'),
    path('grades/history/', views.grade_upload_history, name='grade_upload_history'),
    path('grades/clear-history/', views.clear_grade_history, name='clear_grade_history'),
    path('apply-now/', views.apply_now, name='apply_now'),
    path('test-email/', test_email, name='test_email'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
