from django.contrib import admin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField
import shortuuid




class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        user = self.model(
            email=email
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email
        )
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=False, unique=True)
    phone_number = models.CharField(max_length=255, null=False)
    invited_by = models.IntegerField(null=True)
    photo = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class PropertyTags(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    color = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_tags'


class Property(models.Model):
    cad_acct = models.CharField(max_length=255, null=True)
    gma_tag = models.CharField(max_length=255, null=True)
    property_address = models.CharField(max_length=255, null=True)
    # owner_name = models.CharField(max_length=255,null=True)
    # owner_address = models.CharField(max_length=255,null=True)

    # A property can have multiple owner
    owner_info = JSONField(default=list)

    # place id must be null because user can upload property by csv import
    google_place_id = models.CharField(max_length=255, null=True, unique=True)
    lat = models.CharField(max_length=255, null=True)
    lon = models.CharField(max_length=255, null=True)
    property_tags = models.ManyToManyField(PropertyTags, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'properties'


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_driving = models.BooleanField(default=False)
    angle = models.DecimalField(max_digits=9, decimal_places=6, default=90)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_locations'


class UserVerifications(models.Model):
    code = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    verification_type = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_verifications'


class PropertyNotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255,null=True)
    notes = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_notes'


class PropertyPhotos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    photo_url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_photos'


class UserList(models.Model):
    name = models.CharField(max_length=255, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    leads_count = models.IntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_lists'


class ListProperties(models.Model):
    list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    property_address = models.CharField(max_length=255, null=True)
    cad_acct = models.CharField(max_length=255, null=True)
    gma_tag = models.IntegerField(null=True)
    latitude = models.DecimalField(max_digits=20, decimal_places=16)
    longitude = models.DecimalField(max_digits=20, decimal_places=16)
    tag = models.ForeignKey(PropertyTags, on_delete=models.CASCADE, null=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # A property can have multiple owner
    owner_info = JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'list_properties'


class UserDriver(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=9, decimal_places=6)
    travel_shape = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_drivers'


class UserOwnershipUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_ownership_usages'


class VisitedProperties(models.Model):
    drive = models.ForeignKey(UserDriver, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'visited_properties'


class UserSockets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    socket_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_connected = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_sockets'

def generate_shortuuid():
    shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
    gUid = str(shortuuid.random(length=16))
    return gUid

class Invitations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, null=False)
    status = models.IntegerField(null=True) # invited => 0,in progress =>1,done =>3
    invitation_key = models.CharField(max_length=200, unique=True, default=generate_shortuuid)
    first_name = models.CharField(max_length=255,null=True)
    last_name = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invitations'

class Scout(models.Model):
    first_name = models.CharField(max_length=255,null=True)
    last_name = models.CharField(max_length=255,null=True)
    url = models.CharField(max_length=255,null=True)
    manager_id = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scouts'

class ScoutsListProperty(models.Model):
    scout = models.ForeignKey(Scout,on_delete=models.CASCADE)
    list_properties = models.ForeignKey(ListProperties,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scouts_list_properties'

admin.site.register(User)
admin.site.register(UserSockets)
admin.site.register(UserLocation)
admin.site.register(UserDriver)
