from django.shortcuts import render, get_object_or_404,redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.messages import get_messages

from .forms import ContactForm, ProfilePictureForm,LoginForm, CustomUserCreationForm, StudentProfileForm, TeacherProfileForm, NoteForm,AssignmentForm,SubmissionForm, FeePaymentForm,LeaveRequestForm,SubjectGradeForm,AdmissionApplicationForm
from .models import Event, StudentDashboardProfile,  TeacherProfile, Note, StudentProfile, ClassSubject, StudentClass, Assignment,Submission,Payment,ClassFee,StudentFee,LeaveRequest,SubjectGrade,AdmissionApplication
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import authenticate, login
from django.utils.text import slugify

from collections import defaultdict
import random
import requests
import uuid

from django.utils.dateparse import parse_date
from django.utils import timezone  
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import CustomUser



User = get_user_model()
def home(request):
    return render(request, 'core/home.html')


def about_view(request):
    return render(request, 'core/about.html')


#contact us

def contact_view(request):
    form = ContactForm()
    success = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactForm()
    return render(request, 'core/contact.html', {'form': form, 'success': success})


def events_view(request):
    events = Event.objects.all()
    return render(request, 'core/events.html', {'events': events})

def event_detail_view(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'core/event_detail.html', {'event': event})

#register



def register(request):
    if request.method == 'POST':
        print("DEBUG: Form submitted")  # Debug 1
        role = request.POST.get('role', 'student')
    else:
        role = request.GET.get('role', 'student')  # handle initial load better

    user_form = CustomUserCreationForm(request.POST or None)
    if role == 'student':
        profile_form = StudentProfileForm(request.POST or None)
        profile_form.fields['student_class'].required = True
    else:
        profile_form = TeacherProfileForm(request.POST or None)

    classes = StudentClass.objects.all() if role == 'student' else None

    if request.method == 'POST':
        print("DEBUG: POST request received")  # Debug 2

        if user_form.is_valid() and profile_form.is_valid():
            print("DEBUG: Both forms are valid")  # Debug 3

            # ✅ ADMISSION NUMBER VALIDATION (Only for students)
            if role == 'student':
                entered_admission_number = user_form.cleaned_data.get('admission_number')
                try:
                    approved_application = AdmissionApplication.objects.get(
                        admission_number=entered_admission_number,
                        status='approved'
                    )
                    print("✅ Admission number matched approved application.")
                except AdmissionApplication.DoesNotExist:
                    messages.error(request, "Invalid or unapproved admission number.")
                    return render(request, 'core/register.html', {
                        'user_form': user_form,
                        'profile_form': profile_form,
                        'role': role,
                        'classes': classes
                    })

            user = user_form.save(commit=False)
            username_base = slugify(f"{user_form.cleaned_data['first_name']}{user_form.cleaned_data['last_name']}")
            user.username = f"{username_base}{random.randint(1000, 9999)}"
            user.role = role
            user.save()
            print(f"DEBUG: User created - ID: {user.id}, Role: {user.role}")  # Debug 4

            if role == 'teacher':
                user.admission_number = None  # Will trigger auto-generation
            user.save()

            if role == 'student':
                print("DEBUG: Creating student profile")  # Debug 5
                if not profile_form.cleaned_data.get('student_class'):
                    messages.error(request, "Please select a class for student registration")
                    return render(request, 'core/register.html', {
                        'user_form': user_form,
                        'profile_form': profile_form,
                        'role': role,
                        'classes': classes
                    })

                StudentProfile.objects.create(
                    user=user,
                    student_class=profile_form.cleaned_data['student_class'],
                    admission_number=user.admission_number
                )
            else:
                print("DEBUG: Creating teacher profile")  # Debug 6
                TeacherProfile.objects.create(
                    user=user,
                    subject=profile_form.cleaned_data['subject'],
                    employee_id=f"EMP{user.id:04}"
                )

            user = CustomUser.objects.get(pk=user.pk)
            print(f"DEBUG: User refreshed - ID: {user.id}")  # Debug 7

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            print("DEBUG: User logged in")  # Debug 8

            messages.success(request, "Registration successful!")
            print(f"DEBUG: User role: {user.role}")  # Debug 9

            if user.role == 'teacher':
                print("DEBUG: Redirecting to teacher dashboard")  # Debug 10
                return redirect('teacher_dashboard')
            else:
                print("DEBUG: Redirecting to student dashboard")  # Debug 11
                return redirect('student_dashboard')

        else:
            print("DEBUG: Form validation failed")  # Debug 12
            print("User form errors:", user_form.errors)
            print("Profile form errors:", profile_form.errors)
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(request, 'core/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'role': role,
        'classes': classes
    })
  
@login_required
def student_profile_view(request):
    profile = None 
    try:
        profile = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        default_class, created = StudentClass.objects.get_or_create(grade='P1', defaults={'name': 'Primary 1'})
        messages.info(request, "A new student profile was created for you.")

    if request.method == 'POST':
        pic_form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        profile_form = StudentProfileForm(request.POST, instance=profile)

        if 'upload' in request.POST:
            if pic_form.is_valid():
                pic_form.save()
                messages.success(request, "Profile picture updated successfully!")
        elif 'delete' in request.POST:
            profile.profile_picture.delete(save=True)
            messages.success(request, "Profile picture removed!")
        elif 'update_info' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")

        return redirect('student_profile')

    else:
        pic_form = ProfilePictureForm(instance=profile)
        profile_form = StudentProfileForm(instance=profile)

    return render(request, 'core/student_profile.html', {
        'profile': profile,
        'pic_form': pic_form,
        'profile_form': profile_form
    })



#dashboard


def student_dashboard(request):
    first_name = request.user.first_name

    # Fetch or create the student's dashboard profile
    profile, created = StudentDashboardProfile.objects.get_or_create(user=request.user)

    # Get the student's class
    try:
        student_profile = request.user.studentprofile
        student_class = student_profile.student_class
    except StudentProfile.DoesNotExist:
        return render(request, 'core/unauthorized.html', {'error': 'Student profile not found.'})
    

    # Get approved grades for the student
    grades = SubjectGrade.objects.filter(student=request.user, is_approved=True)


    # Filter assignments by the student's class
    assignments = Assignment.objects.filter(assigned_class=student_class)
    

    # Filter notes by the student's class
    notes = Note.objects.filter(target_class=student_class).order_by('-timestamp')

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        return redirect('student_dashboard')

    return render(request, 'core/student_dashboard.html', {
        'assignments': assignments,
        'notes': notes,
        'profile': profile,
        'first_name': first_name,
        'grades': grades,
    })
#login
def login_view(request):
    if request.method == 'GET':
        storage = get_messages(request)
        for _ in storage:
            pass 

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate using email
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                
                if user.role == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})
#courses
# views.py
@login_required
def my_courses(request):
    try:
        student_profile = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        return render(request, 'core/unauthorized.html', {'error': 'Student profile not found.'})

    if not student_profile.student_class:
        messages.warning(request, "You haven't been assigned to a class yet.")
        return render(request, 'core/my_courses.html', {
            'courses': [],
            'student_class': None
        })

    courses = ClassSubject.objects.filter(student_class=student_profile.student_class)

    return render(request, 'core/my_courses.html', {
        'courses': courses,
        'student_class': student_profile.student_class
    })

# views.py

#teacher dashboard    
@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        return render(request, 'core/unauthorized.html', status=403)
    return render(request, 'core/teacher_dashboard.html')

#teacher profile 
# views.py

@login_required
def teacher_profile(request):
    # Get or create a TeacherProfile for the current user
    profile, created = TeacherProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('teacher_profile')  # Reload page to show updates
    else:
        form = TeacherProfileForm(instance=profile)

    context = {
        'profile': profile,
        'form': form,
        'user': request.user,
    }
    return render(request, 'core/teacher_profile.html', context)  # ✅ matches your current file

#upload note
#teachers 
@login_required
def upload_note(request):
    if request.user.role != 'teacher':
        return render(request, 'core/unauthorized.html', status=403)

    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            # Get form data
            subject_name = form.cleaned_data['subject_name']
            target_class = form.cleaned_data['target_class']
            
            try:
                # Get or create ClassSubject - THIS IS THE CRUCIAL FIX
                class_subject, created = ClassSubject.objects.get_or_create(
                    name=subject_name,
                    student_class=target_class
                )
                
                # Create Note instance
                note = Note(
                    title=form.cleaned_data['title'],
                    subject=class_subject,
                    target_class=target_class,
                    file=form.cleaned_data['file'],
                    description=form.cleaned_data['description'],
                    teacher=request.user
                )
                note.save()
                
                return redirect('teacher_notes')
                
            except Exception as e:
                form.add_error(None, f"Error creating note: {str(e)}")
    else:
        form = NoteForm()
    
    return render(request, 'core/upload_note.html', {'form': form})
@login_required
def teacher_notes(request):
    if request.user.role != 'teacher':
        return render(request, 'core/unauthorized.html', status=403)

    notes = Note.objects.filter(teacher=request.user)
    return render(request, 'core/teacher_notes.html', {'notes': notes})


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, teacher=request.user)
    note.delete()
    return redirect('teacher_notes')


@login_required
def clear_all_notes(request):
    Note.objects.filter(teacher=request.user).delete()
    return redirect('teacher_notes')




#student 
@login_required
def student_notes(request):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    student_class = request.user.studentprofile.student_class
    print("Student class:", student_class.id, student_class.name)
    notes = Note.objects.filter(target_class=student_class).order_by('-timestamp')
    print("Notes found:", notes.count())
    return render(request, 'core/student_notes.html', {'notes': notes  })


@login_required
def view_note_detail(request, note_id):
    
    note = get_object_or_404(Note, id=note_id)

    if request.user.role != 'student' or note.target_class != request.user.studentprofile.student_class:
        return render(request, 'core/unauthorized.html', status=403)

    return render(request, 'core/note_detail.html', {'note': note})



#assignment 


@login_required
def create_assignment(request):
    if request.user.role != 'teacher':
        return render(request, 'core/unauthorized.html', status=403)

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()
            return redirect('my_assignments')
    else:
        form = AssignmentForm()

    return render(request, 'core/create_assignment.html', {
        'form': form
    })


@login_required
def my_assignments(request):
    if request.user.role != 'teacher':
        return render(request, 'core/unauthorized.html', status=403)

    # Get all assignments created by this teacher
    assignments = Assignment.objects.filter(teacher=request.user).order_by('-due_date')

    if 'delete' in request.GET:
        assignment_id = request.GET.get('delete')
        assignment = get_object_or_404(Assignment, id=assignment_id, teacher=request.user)
        assignment.delete()
        return redirect('my_assignments')

    if 'clear_all' in request.POST:
        Assignment.objects.filter(teacher=request.user).delete()
        return redirect('my_assignments')

    return render(request, 'core/my_assignments.html', {
        'assignments': assignments
    })



@login_required
def teacher_view_submissions(request, assignment_id):
    if request.user.role != 'teacher':
        return render(request, 'core/unauthorized.html', status=403)

    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_on')

    return render(request, 'core/teacher_view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
    })





#student assignment 
@login_required
def student_assignments(request):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    try:
        student_profile = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        return render(request, 'core/unauthorized.html', {'error': 'Student profile not found.'})

    # Get all assignments for the student's class
    assignments = Assignment.objects.filter(assigned_class=student_profile.student_class)

    return render(request, 'core/student_assignments.html', {
        'assignments': assignments
    })



@login_required
def assignment_detail_student(request, assignment_id):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    try:
        student_profile = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        return render(request, 'core/unauthorized.html', {'error': 'Student profile not found.'})

    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Check if assignment is for student's class
    if assignment.assigned_class != student_profile.student_class:
        return render(request, 'core/unauthorized.html', {
            'error': f'This assignment is for {assignment.assigned_class}, but you are in {student_profile.student_class}'
        })

    return render(request, 'core/assignment_detail_student.html', {
        'assignment': assignment
    })





@login_required
def submit_assignment(request, assignment_id):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    assignment = get_object_or_404(Assignment, id=assignment_id)

    try:
        student_profile = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        return render(request, 'core/unauthorized.html', {'error': 'Student profile not found.'})

    # Check if due date has passed
    if assignment.due_date < timezone.now().date():
        return render(request, 'core/unauthorized.html', {
            'error': 'You can no longer submit this assignment. Due date has passed.'
        })

    # Check if student already submitted
    submission, created = Submission.objects.get_or_create(
        student=request.user,
        assignment=assignment,
        defaults={'file': None}
    )

    form = SubmissionForm(instance=submission)

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment resubmitted successfully.")
            return redirect('student_assignments')
    
    return render(request, 'core/submit_assignment.html', {
        'form': form,
        'assignment': assignment,
        'submission': submission,
        'created': created
    })


@login_required
def view_submission_student(request, assignment_id):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    submission = get_object_or_404(Submission, assignment__id=assignment_id, student=request.user)

    assignment = submission.assignment
    current_date = timezone.now().date()

    can_edit = assignment.due_date >= current_date

    return render(request, 'core/view_submission_student.html', {
        'submission': submission,
        'can_edit': can_edit
    })






@login_required
def delete_submission(request, assignment_id):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    submission = get_object_or_404(Submission, student=request.user, assignment__id=assignment_id)

    # Prevent deletion after due date
    if submission.assignment.due_date < timezone.now().date():
        messages.error(request, "You cannot delete this submission. The due date has passed.")
        return redirect('submit_assignment', assignment_id=assignment_id)

    # Delete file from storage
    if submission.file:
        submission.file.delete()

    submission.delete()
    messages.success(request, "Your submission has been deleted successfully.")

    return redirect('submit_assignment', assignment_id=assignment_id)


@login_required
def pay_fees(request):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    try:
        student_profile = request.user.studentprofile
        class_fee = ClassFee.objects.get(student_class=student_profile.student_class)
    except (StudentProfile.DoesNotExist, ClassFee.DoesNotExist):
        messages.error(request, "Your class or fee info isn't set up yet.")
        return redirect('student_dashboard')

    # Get or create StudentFee record
    student_fee, created = StudentFee.objects.get_or_create(
        student=request.user,
        defaults={'class_fee': class_fee}
    )

    if student_fee.status == 'paid':
        messages.info(request, "You have completed all required fees.")
        return redirect('payment_receipt')

    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            email = request.user.email
            reference = str(uuid.uuid4())

            
            


            # Update local payment tracking
            student_fee.paid_amount += amount
            student_fee.update_status()
            student_fee.save()

            # Prepare Paystack request
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "email": email,
                "amount": int(amount * 100),  # Convert to kobo
                "reference": reference,
                "callback_url": request.build_absolute_uri('/payment/verify/')
            }

            response = requests.post(settings.PAYSTACK_PAYMENT_URL, json=data, headers=headers)

            if response.status_code == 200:
                # Save payment record
                Payment.objects.create(
                    student=request.user,
                    amount=amount,
                    reference=reference,
                    status='initialized'
                )
                return redirect(response.json()['data']['authorization_url'])
            else:
                messages.error(request, "Something went wrong with Paystack.")

    else:
        remaining_balance = student_fee.balance()
        form = FeePaymentForm(initial={'amount': min(remaining_balance, 50000)})

    return render(request, 'core/pay_fees.html', {
        'form': form,
        'fee_info': student_fee
    })

@login_required
def verify_payment(request):
    ref = request.GET.get('reference')
    url = f"{settings.PAYSTACK_VERIFY_URL}{ref}"

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if data['status'] and data['data']['status'] == 'success':
        try:
            payment = Payment.objects.get(reference=ref)
            student_fee = StudentFee.objects.get(student=payment.student)
            
            # Ensure no overpayment
            balance = student_fee.balance()
            actual_paid = data['data']['amount'] / 100  # Convert from kobo to Naira
            effective_payment = min(actual_paid, balance + actual_paid - balance)
            
            # Update local records
            payment.amount = effective_payment
            payment.status = 'paid'
            payment.receipt_url = data['data'].get('receipt_url')
            payment.save()

            student_fee.paid_amount += effective_payment
            student_fee.update_status()
            student_fee.save()

            messages.success(request, "Payment successful!")

        except Exception as e:
            messages.error(request, f"Error updating payment: {e}")
    else:
        messages.error(request, "Payment verification failed.")

    return redirect('payment_receipt')

@login_required
def payment_receipt(request):
    payments = Payment.objects.filter(student=request.user).order_by('-paid_at')
    
    try:
        student_fee = StudentFee.objects.get(student=request.user)
    except StudentFee.DoesNotExist:
        student_fee = None

    return render(request, 'core/payment_receipt.html', {
        'payments': payments,
        'student_fee': student_fee
    })


@login_required
def clear_payment_history(request):
    if request.user.role != 'student':
        return render(request, 'core/unauthorized.html', status=403)

    # Delete all payments for this student
    Payment.objects.filter(student=request.user).delete()

    messages.success(request, "Your payment history has been cleared.")
    return redirect('payment_receipt')

#leave


@login_required
def request_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.teacher = request.user
            leave.save()
            return redirect('leave_status')
    else:
        form = LeaveRequestForm()

    return render(request, 'core/request_leave.html', {'form': form})


@login_required
def leave_status(request):
    leaves = LeaveRequest.objects.filter(teacher=request.user).order_by('-submitted_at')
    return render(request, 'core/leave_status.html', {'leaves': leaves})




@staff_member_required
def admin_leave_list(request):
    leaves = LeaveRequest.objects.all().order_by('-submitted_at')
    return render(request, 'core/admin_leave_list.html', {'leaves': leaves})


@staff_member_required
def approve_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'approved'
    leave.save()
    return redirect('admin_leave_list')

@staff_member_required
def decline_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'declined'
    leave.save()
    return redirect('admin_leave_list')

#grading


# views.py



@login_required
def upload_grade(request):
    selected_class = None

    if request.method == 'POST':
        # Process grade submission
        class_id = request.POST.get('student_class')
        if class_id:
            try:
                selected_class = StudentClass.objects.get(id=class_id)
            except StudentClass.DoesNotExist:
                selected_class = None

        form = SubjectGradeForm(request.POST, selected_class=selected_class)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.submitted_by = request.user
            grade.save()
            return redirect('grade_upload_history')  # Or show success message
    else:
        # GET request to select class
        class_id = request.GET.get('student_class')
        if class_id:
            try:
                selected_class = StudentClass.objects.get(id=class_id)
            except StudentClass.DoesNotExist:
                selected_class = None

        form = SubjectGradeForm(selected_class=selected_class)

    return render(request, 'core/upload_grade.html', {
        'form': form,
        'selected_class': selected_class,
    })


@login_required
def clear_grade_history(request):
    if request.method == 'POST':
        SubjectGrade.objects.filter(submitted_by=request.user).delete()
        return redirect('grade_upload_history')
    return redirect('grade_upload_history')




@login_required
def grade_upload_history(request):
    grades = SubjectGrade.objects.filter(submitted_by=request.user).order_by('-created_at')
    return render(request, 'core/grade_upload_history.html', {'grades': grades})






@login_required
def view_result(request):
    grades = SubjectGrade.objects.filter(
        student=request.user,
        is_approved=True
    ).order_by('session', 'term', 'subject')

    results = defaultdict(list)
    seen_subjects = set()

    for grade in grades:
        key = f"{grade.session.strip()} - {grade.term.strip()}"
        # Avoid repeating the same subject
        unique_id = f"{key}-{grade.subject.strip().lower()}"
        if unique_id not in seen_subjects:
            results[key].append(grade)
            seen_subjects.add(unique_id)

    return render(request, 'core/student_result.html', {'results': dict(results)})


#apply now 


 
def apply_now(request):
    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You have applied successfully. Please wait for an email update.")
            return redirect('apply_now')
    else:
        form = AdmissionApplicationForm()
    return render(request, 'core/apply_now.html', {'form': form})





from django.core.mail import send_mail
from django.http import HttpResponse

def test_email(request):
    send_mail(
        subject='Test Admission Email',
        message='Congratulations! This is a test email from your Django app.',
        from_email='mayowasammy2@gmail.com',
        recipient_list=['mayowad19@gmail.com'],  # change to your test email
        fail_silently=False,
    )
    return HttpResponse("Email sent successfully.")
