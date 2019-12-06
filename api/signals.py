from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import *

@receiver(post_save, sender=Property)
def property_post_save(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            user_id = Property.objects.get(id=instance.id).user_list.user.id
            user = User.objects.get(id = user_id)
            activityLog = ActivityLog.objects.create(user=user,type = 'insert',activity= 'property', message='inserted a property', activity_id=instance.id)
            activityLog.save()
        else:
            user_id = Property.objects.get(id=instance.id).user_list.user.id
            user = User.objects.get(id = user_id)
            activityLog = ActivityLog.objects.create(user=user,type = 'update',activity='property', message='updated a property', activity_id = instance.id)
            activityLog.save()
    except :
        print('Error while property post save')

@receiver(post_save, sender=History)
def history_post_save(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            user_id = History.objects.get(id=instance.id).user.id
            user = User.objects.get(id = user_id)
            activityLog = ActivityLog.objects.create(user=user, type = 'insert', activity= 'history', message='started driving', activity_id=instance.id)
            activityLog.save()
        else:
            user_id = History.objects.get(id=instance.id).user.id
            user = User.objects.get(id = user_id)
            activityLog = ActivityLog.objects.create(user=user, type = 'update', activity='history', message='ended driving', activity_id=instance.id)
            activityLog.save()
    except :
        print('Error while history post save')

@receiver(post_save, sender=PropertyPhotos)
def property_photos_post_save(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            property_photo = PropertyPhotos.objects.get(id=instance.id)
            user_id = property_photo.user.id
            property = property_photo.property
            user = User.objects.get(id = user_id)
            activityLog = ActivityLog.objects.create(user=user,type = 'insert',activity='property', message= 'inserted a photo to a property', activity_id=property.id)
            activityLog.save()
    except :
        print('Error while photo post save')

@receiver(post_save, sender=PropertyNotes)
def property_notes_post_save(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            property_note = PropertyNotes.objects.get(id=instance.id)
            user = property_note.user
            property = property_note.property
            activityLog = ActivityLog.objects.create(user=user,type = 'insert',activity='property', message= 'inserted a note to a property', activity_id=property.id)
            activityLog.save()
        else:
            property_note = PropertyNotes.objects.get(id=instance.id)
            user = property_note.user
            activityLog = ActivityLog.objects.create(user=user,type = 'update',activity = 'property', message='updated a note to a property', activity_id=instance.id)
            activityLog.save()
    except :
        print('Error while note post save')

@receiver(post_save, sender=Invitations)
def invitation_post_save(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            invitation = Invitations.objects.get(id = instance.id)
            user = invitation.user
            activityLog = ActivityLog.objects.create(user=user,type = 'insert',activity='invitation', message= 'invited '+instance.email+' to team', activity_id=instance.id)
            activityLog.save()
    except :
        print('Error while invitation post save')

@receiver(post_save, sender=User)
def TeamMemberRegistration(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            team = User.objects.get(id = instance.id)
            print('------------')
            print(team.invited_by)
            if team.invited_by:
                activityLog = ActivityLog.objects.create(user=team,type = 'insert',activity='user', message= 'accepted the invitaion to team', activity_id=instance.id)
                activityLog.save()
            else :
                activityLog = ActivityLog.objects.create(user=team,type = 'insert',activity='user', message= 'registered a new account', activity_id=instance.id)
                activityLog.save()
    except :
        print('Error while invitation post save')

@receiver(post_save, sender=UserList)
def user_list_post_save(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            user_list = UserList.objects.get(id = instance.id)
            user = user_list.user
            activityLog = ActivityLog.objects.create(user=user,type = 'insert',activity='list', message= 'created a list', activity_id=instance.id)
            activityLog.save()
    except :
        print('Error while user_list post save')


@receiver(post_save, sender=Scout)
def scout_post_save(sender, instance, created, update_fields, **kwargs):
    try :
        if created:
            scout = Scout.objects.get(id = instance.id)
            user = scout.manager_id
            activityLog = ActivityLog.objects.create(user=user,type = 'insert',activity='scout', message= 'created a scout', activity_id=instance.id)
            activityLog.save()
    except :
        print('Error while scout post save')