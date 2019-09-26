from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

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

    def to_representation(self, instance):
        # instance is the model object. create the custom json format by accessing instance attributes normaly and return it

        identifiers = dict()
        identifiers['color_name'] = instance.color
        identifiers['color_code'] = instance.color_code

        representation = {
            'id' : instance.id,
            'name' : instance.name,
            'color': identifiers,
            'user': instance.user.id,
            'created_at': instance.created_at,
            'updated_at' : instance.updated_at
        }

        return representation

class PropertyNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyNotes
        fields = '__all__'


class PropertyPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyPhotos
        # fields = ['user','property','photo_url']
        fields ='__all__'

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        fields = '__all__'


class ListPropertiesSerializer(serializers.ModelSerializer):
    # property = PrimaryKeyRelatedField(read_only=True)
    photo_count = serializers.IntegerField(read_only=True, default=0)
    note_count = serializers.IntegerField(read_only=True, default=0)
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


class UserSocketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSockets
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    # property_photos = PropertyPhotosSerializer(many=True,read_only=True)

    class Meta:
        model = Property
        # fields = ['id','cad_acct','gma_tag','property_address','owner_name','owner_address','property_photos']
        fields ='__all__'

class InvitationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitations
        fields = '__all__'

class ScoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scout
        fields = '__all__'

class ScoutsListPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutsListProperty
        fields = '__all__'

class AssignMemberToListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignMemberToList
        fields = '__all__'