"""
This file creates a token object for each and every user 
that will be created and this signal.py will be imported 
by the apps.py file in the ready function.
"""

from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
 
#brief: This function will run whenever we create a superuser
@receiver(post_save, sender=User)           
def create_token(sender, instance, created, **kwargs):
    print("INSIDE CERATETOEKNEN")
    if created:
        token = Token.objects.create(user=instance)
        token.save()
        print("CREATED TOKENNNNNN")
    print("CREATED TOKENNNNNN OUTSIDE")
    