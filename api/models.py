from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email_address = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    invited_by = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'


class UserLocation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    lattitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_driving = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_location'


class UserVerifications(models.Model):
    code = models.TextField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    verification_type = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_verifications'


class PropertyTags(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    color = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_tags'


class PropertyNotes(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    property_id = models.IntegerField(null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    notes = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_notes'


class PropertyPhotos(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    property_id = models.IntegerField(null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    photo_url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_photos'


class UserList(models.Model):
    name = models.CharField(max_length=255, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    leads_count = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_list'


class ListProperties(models.Model):
    list_id = models.ForeignKey(UserList, on_delete=models.CASCADE)
    property_address = models.CharField(max_length=255, null=True)
    cad_acct = models.CharField(max_length=255, null=True)
    gma_tag = models.IntegerField(null=True)
    lattitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    tag_id = models.ForeignKey(PropertyTags, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'list_properties'


class UserDriver(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    list_id = models.ForeignKey(UserList, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=9, decimal_places=6)
    travel_shape = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_drives'


class UserOwnershipUsage(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    property_id = models.IntegerField(null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_ownership_usage'


class VisitedProperties(models.Model):
    drive_id = models.ForeignKey(UserDriver, on_delete=models.CASCADE)
    property_id = models.IntegerField(null=True)  # models.ForeignKey(, unique=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'visited_properties'
