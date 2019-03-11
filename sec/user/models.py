from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.TextField(max_length=50, blank=True)
    phone_number = models.TextField(max_length=50, blank=True)
    street_address = models.TextField(max_length=50, blank=True)
    city = models.TextField(max_length=50, blank=True)
    state = models.TextField(max_length=50, blank=True)
    postal_code = models.TextField(max_length=50, blank=True)
    country = models.TextField(max_length=50, blank=True)
    categories = models.ManyToManyField('projects.ProjectCategory', related_name='competance_categories')
    security_question = models.TextField(max_length=254, blank=False)
    security_question_answer = models.TextField(max_length=254, blank=False)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()