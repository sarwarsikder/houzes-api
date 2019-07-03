from rest_framework import serializers
from api.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = '__all__'


class UserVerificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerifications
        fields = '__all__'


class PropertyTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyTags
        fields = '__all__'


class PropertyNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyNotes
        fields = '__all__'


class PropertyPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyPhotos
        fields = '__all__'


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        fields = '__all__'


class ListPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListProperties
        fields = '__all__'


class UserDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDriver
        fields = '__all__'


class UserOwnershipUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOwnershipUsage
        fields = '__all__'


class VisitedPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitedProperties
        fields = '__all__'
