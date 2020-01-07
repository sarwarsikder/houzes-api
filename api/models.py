import shortuuid
from django.contrib import admin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.conf import settings
from reportlab.platypus.doctemplate import onDrawStr


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


def generate_shortuuid():
    shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
    gUid = str(shortuuid.random(length=16))
    return gUid


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=False, unique=True)
    phone_number = models.CharField(max_length=255, null=False)
    invited_by = models.IntegerField(null=True)
    photo = models.TextField(null=True)
    upgrade = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)

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
    color_code = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_tags'


#
# class Property(models.Model):
#     cad_acct = models.CharField(max_length=255, null=True)
#     gma_tag = models.CharField(max_length=255, null=True)
#     property_address = models.CharField(max_length=255, null=True)
#     # owner_name = models.CharField(max_length=255,null=True)
#     # owner_address = models.CharField(max_length=255,null=True)
#
#     # A property can have multiple owner
#     owner_info = JSONField(default=list)
#
#     # place id must be null because user can upload property by csv import
#     google_place_id = models.CharField(max_length=255, null=True, unique=True)
#     latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
#     longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
#     property_tags = JSONField(default=list)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'properties'


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


class UserList(models.Model):
    name = models.CharField(max_length=255, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    leads_count = models.IntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_lists'


class Property(models.Model):
    user_list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    street = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    zip = models.CharField(max_length=255, null=True)
    cad_acct = models.CharField(max_length=255, null=True)
    gma_tag = models.IntegerField(null=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    property_tags = JSONField(default=list)
    power_trace_request_id = models.IntegerField(null=True)
    # A property can have multiple owner
    owner_info = JSONField(default=list, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'properties'


class PropertyNotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True)
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
    thumb_photo_url = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_photos'


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


class Invitations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    email = models.CharField(max_length=255, null=False)
    status = models.IntegerField(null=True)  # invited => 0,in progress =>1,done =>3
    invitation_key = models.CharField(max_length=200, unique=True, default=generate_shortuuid)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invitations'


class Scout(models.Model):
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    manager_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scouts'


class ScoutUserList(models.Model):
    scout = models.ForeignKey(Scout, on_delete=models.CASCADE)
    user_list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scouts_user_lists'


class AssignMemberToList(models.Model):
    list = models.ForeignKey(UserList, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assign_member_to_list'


class History(models.Model):
    start_point_latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    start_point_longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    end_point_latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    end_point_longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    image = models.CharField(max_length=255, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    polylines = models.TextField(null=True)
    length = models.DecimalField(max_digits=50, decimal_places=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'history'


class HistoryDetail(models.Model):
    history = models.ForeignKey(History, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'history_details'


class ForgetPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link_key = models.CharField(max_length=200, unique=True, default=generate_shortuuid)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'forget_password'


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=255, null=True)
    activity_id = models.IntegerField(null=True)
    message = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activity_logs'


class GetNeighborhood(models.Model):
    neighbor_address = models.CharField(max_length=50, null=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    ownership_info_request_id = models.IntegerField(null=True)
    ownership_info = JSONField(default=dict)
    power_trace = JSONField(default=dict)
    power_trace_request_id = models.IntegerField(null=True)
    owner_status = models.CharField(max_length=50, default=None, null=True)
    power_trace_status = models.CharField(max_length=50, default=None, null=True)
    status = models.CharField(max_length=50, default=None, null=True)
    is_power_trace_requested = models.BooleanField(default=False)
    is_owner_info_requested = models.BooleanField(default=False)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'get_neighborhoods'


class Plans(models.Model):
    plan_name = models.CharField(max_length=500, null=True)
    plan_cost = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    plan_coin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='%(class)s_requests_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plans'


class PaymentPlan(models.Model):
    payment_plan_name = models.CharField(max_length=500, null=True)
    payment_plan_coin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='%(class)s_requests_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_plans'


class UpgradeProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # wallet = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'upgrade_profiles'


class PaymentTransaction(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE)
    transaction_coin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_by = models.ForeignKey(User,
                                   null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_transactions'


class UpgradeHistory(models.Model):
    upgrade_profile = models.ForeignKey(UpgradeProfile, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    transaction_coin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    transaction_json = JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'upgrade_histories'


class MailWizardSubsType(models.Model):
    type_name = models.CharField(max_length=500, null=True)
    days_interval = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_wizard_subs_types'


class MailWizardInfo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    subs_type = models.ForeignKey(MailWizardSubsType, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_wizard_info'


admin.site.register(User)
admin.site.register(UserSockets)
admin.site.register(UserLocation)
admin.site.register(UserDriver)
