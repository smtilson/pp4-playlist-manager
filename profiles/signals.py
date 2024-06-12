from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        email = instance.email
        password = instance.password
        # The bio field is not set because the User instance has not bio attribute by default.
        # But you can still update this attribute with the profile detail form.
        Profile.objects.create(user=instance, email=email,password=password)