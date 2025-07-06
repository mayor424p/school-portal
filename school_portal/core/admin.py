from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Event, ContactMessage, CustomUser, StudentProfile, TeacherProfile,Subject,ClassSubject,StudentClass,ClassFee,SubjectGrade,TermResult,AdmissionApplication


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date_sent', 'was_recent')
    readonly_fields = ('name', 'email', 'message', 'date_sent')
    list_filter = ('date_sent',)
    date_hierarchy = 'date_sent'
    search_fields = ('name', 'email', 'message')

    @admin.display(boolean=True, description='Recent?')
    def was_recent(self, obj):
        return obj.date_sent >= timezone.now() - timezone.timedelta(days=1)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_posted', 'has_image')
    search_fields = ('title', 'body')
    list_filter = ('date_posted',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('date_posted',)
    date_hierarchy = 'date_posted'

    @admin.display(boolean=True, description='Has Image?')
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'admission_number', 'email', 'first_name', 'last_name',
        'is_staff', 'role_display', 'is_active'
    )
    search_fields = ('admission_number', 'email', 'first_name', 'last_name')
    ordering = ('admission_number',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')
    
    fieldsets = (
        (None, {'fields': ('admission_number', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'middle_name', 'last_name',
                'email', 'date_of_birth', 'role'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'admission_number', 'email', 'first_name',
                'last_name', 'password1', 'password2', 'role'
            ),
        }),
    )

    def get_deleted_objects(self, objs, request):
        
        
        deleted_objects = []
        for obj in objs:
            try:
                str_repr = str(obj)
            except Exception:
                str_repr = f"User {obj.pk}"
            deleted_objects.append(str_repr)
        
        return (
            deleted_objects,
            {},
            "CustomUser",
            "",
        )

    @admin.display(description='Role')
    def role_display(self, obj):
        return dict(CustomUser.ROLE_CHOICES).get(obj.role, obj.role or 'Unknown')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_class', 'profile_picture_display')
    search_fields = (
        'user__admission_number', 'user__first_name',
        'user__last_name', 'student_class'
    )
    raw_id_fields = ('user',)
    list_select_related = ('user',)

    @admin.display(description='Profile Picture')
    def profile_picture_display(self, obj):
        return '✅' if obj.profile_picture else '❌'
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'employee_id', 'is_active_teacher')
    search_fields = (
        'user__admission_number', 'user__first_name',
        'user__last_name', 'subject', 'employee_id'
    )
    list_filter = ('subject', 'user__is_active')
    raw_id_fields = ('user',)
    list_select_related = ('user',)

    @admin.display(boolean=True, description='Active?')
    def is_active_teacher(self, obj):
        return obj.user.is_active
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# admin.py

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'class_teacher')
    search_fields = ('name', 'grade')
    list_filter = ('grade',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_core']
    search_fields = ['name', 'code']

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['student_class', 'subject', 'teacher']
    list_filter = ['student_class__grade', 'subject']
    search_fields = ['subject__name', 'student_class__name']
    autocomplete_fields = ['subject', 'student_class', 'teacher']


@admin.register(ClassFee)
class ClassFeeAdmin(admin.ModelAdmin):
    list_display = ('student_class', 'total_fee')
    search_fields = ['student_class__name']



from django.contrib import admin
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'start_date', 'end_date', 'status', 'submitted_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'subject', 'purpose')
    ordering = ('-submitted_at',)




# admin.py



@admin.register(SubjectGrade)
class SubjectGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'first_ca', 'second_ca', 'third_ca', 'exam', 'total_score', 'term', 'session', 'is_approved', 'created_at')
    list_filter = ('term', 'session', 'is_approved')
    actions = ['approve_selected_grades']

    def approve_selected_grades(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} grade(s) marked as approved.")
    approve_selected_grades.short_description = "Mark selected grades as approved"



@admin.register(TermResult)
class TermResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'session', 'is_published', 'published_at')
    list_filter = ('term', 'session', 'is_published')


#apply now 




@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'class_applying_to', 'status', 'admission_number']
    list_filter = ['status']
    actions = ['approve_applications', 'decline_applications']
    actions_selection_counter = True

    def approve_applications(self, request, queryset):
        print("🛠 Admin approval triggered")

        for app in queryset.filter(status='pending'):
            print(f"Processing application for: {app.full_name} <{app.email}>")

            if not app.email:
                print("⚠️ No email found for applicant. Skipping...")
                continue

            app.status = 'approved'
            app.admission_number = f"ADM{app.id:04d}"  # e.g. ADM0003
            app.save()

            subject = 'Admission Approved'
            message = (
                f"Dear {app.full_name},\n\n"
                f"Congratulations! Your admission has been approved.\n"
                f"Your admission number is: {app.admission_number}.\n\n"
                f"Welcome aboard!"
            )

            try:
                send_mail(
                    subject,
                    message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[app.email],
                    fail_silently=False,
                )
                print(f"✅ Email sent to {app.email}")
            except Exception as e:
                print(f"❌ Failed to send email to {app.email}: {e}")

        self.message_user(request, "✅ Selected applications approved and emails sent.")

    approve_applications.short_description = "✅ Approve & email admission number"

    def decline_applications(self, request, queryset):
        for app in queryset.filter(status='pending'):
            app.status = 'declined'
            app.save()

            subject = 'Admission Application Declined'
            message = (
                f"Dear {app.full_name},\n\n"
                f"We regret to inform you that your admission application has been declined.\n\n"
                f"Thank you for your interest."
            )

            try:
                send_mail(
                    subject,
                    message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[app.email],
                    fail_silently=False,
                )
                print(f"📩 Decline email sent to {app.email}")
            except Exception as e:
                print(f"❌ Failed to send decline email: {e}")

        self.message_user(request, "❌ Selected applications declined and emails sent.")

    decline_applications.short_description = "❌ Decline & send email"
