# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import AdmissionApplication
# from django.core.mail import send_mail

# @receiver(post_save, sender=AdmissionApplication)
# def send_admission_email(sender, instance, created, **kwargs):
#     # Only send if approved and not newly created
#     if not created and instance.status == 'approved':
#         subject = "Your Admission Has Been Approved"
#         message = f"""
# Dear {instance.full_name},

# Congratulations! Your admission to our school has been approved.

# Your Admission Number is: {instance.admission_number}

# You may now proceed to register on our platform using this number.

# Thank you.
# """
#         send_mail(
#             subject,
#             message,
#             'noreply@yourschool.com',
#             [instance.email],
#             fail_silently=False,
#         )
