from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import ContactMessage, StudentProfile, TeacherProfile,CustomUser,StudentClass,Note,Assignment,Submission,LeaveRequest,SubjectGrade
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import AdmissionApplication
import uuid

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Type your message...'}),
        }



class CustomUserCreationForm (UserCreationForm):
    middle_name = forms.CharField(required=False)
    dob = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label="Date of Birth")
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')], required=True)
    admission_number = forms.CharField(required=False, label="Admission Number")  

    class Meta:
        model = CustomUser
        fields = ['first_name', 'middle_name', 'last_name',  'email','admission_number', 'dob', 'role']

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Customize password field help text if needed
            self.fields['password1'].help_text = None
            self.fields['password2'].help_text = "Enter the same password as before, for verification."  

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1, self.instance)
        except ValidationError as error:
            self.add_error('password1', error)
        return password1        

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == 'teacher':
            if 'admission_number' in self.errors:
                del self.errors['admission_number']
            cleaned_data['admission_number'] = None  # Will trigger model generation
    
        return cleaned_data

        
    def clean_admission_number(self):
        admission_number = self.cleaned_data.get('admission_number')
        role = self.cleaned_data.get('role')
        
        # Skip validation for teachers (will be auto-generated)
        if role == 'teacher':
            return None
            
        # For students, require admission number
        if not admission_number:
            raise ValidationError('Admission number is required for students.')
            
        return admission_number
        
    

class StudentProfileForm(forms.ModelForm):
    student_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        empty_label="Select Class",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Class",
        required=False
    )

    class Meta:
        model = StudentProfile
        fields = ['student_class', 'admission_number']
   


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = [ 'subject']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'})
        }

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture']


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )



class NoteForm(forms.ModelForm):
    subject_name = forms.CharField(max_length=100, required=True, label="Subject Name",help_text="Type the subject name (e.g. Mathematics)")
    class Meta:
        model = Note
        fields = ['title', 'description', 'file', 'subject_name', 'target_class']
        widgets = {
            'target_class': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }



class AssignmentForm(forms.ModelForm):
    assigned_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        label="Select Class"
    )
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'file', 'due_date', 'assigned_class']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),  # Add calendar widget
        }



class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']



class FeePaymentForm(forms.Form):
    email = forms.EmailField()
    amount = forms.DecimalField(label="Amount", max_digits=10, decimal_places=2)


# forms.py
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['subject', 'profile_picture']



class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['subject', 'purpose', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }







class SubjectGradeForm(forms.ModelForm):
    student_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        required=False,
        label="Class"
    )

    class Meta:
        model = SubjectGrade
        fields = [
            'student_class',
            'student', 'subject',
            'first_ca', 'second_ca', 'third_ca', 'exam',
            'term', 'session'
        ]

    def __init__(self, *args, **kwargs):
        selected_class = kwargs.pop('selected_class', None)
        super().__init__(*args, **kwargs)

        if selected_class:
            self.fields['student'].queryset = CustomUser.objects.filter(
                role='student',
                studentprofile__student_class=selected_class
            )
        else:
            self.fields['student'].queryset = CustomUser.objects.none()


#apply now 



class AdmissionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = ['full_name', 'email', 'phone', 'address', 'previous_school', 'date_of_birth', 'class_applying_to']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }
