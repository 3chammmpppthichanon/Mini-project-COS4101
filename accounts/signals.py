from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Advisor

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'Student':
            Student.objects.create(user=instance)
        elif instance.role == 'Advisor':
            Advisor.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if instance.role == 'Student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == 'Advisor' and hasattr(instance, 'advisor_profile'):
        instance.advisor_profile.save()