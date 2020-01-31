from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from notifications.models import Notification
from api.models import *
from django.contrib.contenttypes.models import ContentType


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        # instance is the model object. create the custom json format by accessing instance
        # attributes normaly and return it
        #
        # identifiers = dict()
        # identifiers['color_name'] = instance.color
        # identifiers['color_code'] = instance.color_code'
        amount = 0.0
        is_team_invitable = False
        power_trace = 0.0
        owner_info = 0.0
        mailer_wizard = 0.0

        if instance.is_admin:
            upgrade = instance.upgrade
            upgrade_profile = UpgradeProfile.objects.filter(user__id = instance.id).first()
            if upgrade_profile:
                amount = UpgradeProfile.objects.filter(user__id = instance.id).first().coin
        else:
            upgrade_profile = UpgradeProfile.objects.filter(user__id = instance.invited_by).first()
            if User.objects.filter(id = instance.invited_by).first():
                upgrade = User.objects.filter(id = instance.invited_by).first().upgrade
            if upgrade_profile:
                amount = upgrade_profile.coin
        plan = Plans.objects.filter(id=upgrade_profile.plan.id).first()
        if plan.plan_name == 'Team' and instance.is_admin == True:
            is_team_invitable = True

        paymentPlanPowerTrace = PaymentPlan.objects.filter(payment_plan_name = 'power-trace', plan = plan).first()
        if paymentPlanPowerTrace:
            power_trace = paymentPlanPowerTrace.payment_plan_coin
        paymentPlanOwnerInfo = PaymentPlan.objects.filter(payment_plan_name = 'fetch-ownership-info', plan=plan).first()
        if paymentPlanOwnerInfo :
            owner_info = paymentPlanOwnerInfo.payment_plan_coin
        paymentPlanMailerWizard = PaymentPlan.objects.filter(payment_plan_name = 'mailer-wizard', plan=plan).first()
        if paymentPlanMailerWizard :
            mailer_wizard = paymentPlanMailerWizard.payment_plan_coin

        representation = {
            'id' : instance.id,
            'last_login' : instance.last_login,
            'first_name' : instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'phone_number' : instance.phone_number,
            'invited_by' : instance.invited_by,
            'photo' : instance.photo,
            'is_active' : instance.is_active,
            'is_admin' : instance.is_admin,
            'upgrade_info' : {
                'is_team_invitable' : is_team_invitable,
                'amount' : float(amount),
                'power_trace' : float(power_trace),
                'owner_info' : float(owner_info),
                'mailer_wizard' : float(mailer_wizard),
                'plan' : PlanSerializer(plan).data
            },
            'created_at': instance.created_at,
            'updated_at' : instance.updated_at
        }

        return representation


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
        # instance is the model object. create the custom json format by accessing instance
        # attributes normaly and return it

        identifiers = dict()
        identifiers['color_name'] = instance.color
        identifiers['color_code'] = instance.color_code

        try :
            user_id = instance.user.id
        except:
            user_id = None

        representation = {
            'id': instance.id,
            'name': instance.name,
            'color': identifiers,
            'user': user_id ,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
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
        fields = '__all__'


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    # property = PrimaryKeyRelatedField(read_only=True)
    # photo_count = serializers.IntegerField(read_only=True, default=0)
    # note_count = serializers.IntegerField(read_only=True, default=0)
    class Meta:
        model = Property
        fields = '__all__'

    def to_representation(self, instance):
        # instance is the model object. create the custom json format by accessing instance
        # attributes normaly and return it
        try:
            user_list_id = instance.user_list.id
        except:
            user_list_id = None
        try:
            history = HistoryDetail.objects.filter(property__id=instance.id)[0].history.id
        except:
            history =None
        representation = {
            'id' : instance.id,
            'user_list' : user_list_id,
            'street': instance.street,
            'city': instance.city,
            'state': instance.state,
            'zip': instance.zip,
            'cad_acct': instance.cad_acct,
            'gma_tag': instance.gma_tag,
            'latitude' : instance.latitude,
            'longitude' : instance.longitude,
            'property_tags' : instance.property_tags,
            'owner_info' : instance.owner_info,
            'power_trace_request_id' : instance.power_trace_request_id,
            'photo_count' : PropertyPhotos.objects.filter(property=instance).count(),
            'note_count': PropertyNotes.objects.filter(property=instance).count(),
            'history' : history,
            'created_at': instance.created_at,
            'updated_at' : instance.updated_at
        }
        return representation


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


class InvitationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitations
        fields = '__all__'


class ScoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scout
        fields = '__all__'


class ScoutUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutUserList
        fields = '__all__'


class AssignMemberToListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignMemberToList
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'

    def to_representation(self, instance):
        # instance is the model object. create the custom json format by accessing
        # instance attributes normaly and return it

        representation = {
            'id': instance.id,
            'start_point_latitude': instance.start_point_latitude,
            'start_point_longitude': instance.start_point_longitude,
            'end_point_latitude': instance.end_point_latitude,
            'end_point_longitude': instance.end_point_longitude,
            'image': instance.image,
            'start_time': instance.start_time,
            'end_time': instance.end_time,
            'polylines': instance.polylines,
            'length' : instance.length,
            'user' : instance.user.id,
            'property_count': HistoryDetail.objects.filter(history = instance.id).count(),
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }

        return representation


class HistoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryDetail
        fields = '__all__'

    def to_representation(self, instance):

        representation = {
            'id': instance.id,
            'history_detail': HistorySerializer(History.objects.get(id=instance.history.id)).data,
            'property_detail': PropertySerializer(Property.objects.get(id=instance.property.id)).data,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }

        return representation


class ForgetPasswordSerializer(serializers.ModelSerializer):
    class Meta :
        model = ForgetPassword
        fields = '__all__'

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'email': User.objects.get(id= instance.user.id).email,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        return representation


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta :
        model = ActivityLog
        fields = '__all__'

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'user': UserSerializer(User.objects.get(id= instance.user.id)).data,
            'activity' : instance.activity,
            'activity_id' : instance.activity_id,
            'message' : instance.message,
            'type' : instance.type,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        return representation


class GetNeighborhoodSerializer(serializers.ModelSerializer):
    class Meta :
        model = GetNeighborhood
        fields = '__all__'

    def to_representation(self, instance):
        print(':::::::::::OWNERSHIP :::::::::::::::')
        ownership_info = None
        try:
            ownership_info = None if instance.ownership_info=={} else instance.ownership_info['owner_info']
        except:
            ownership_info = None
        representation = {
            'id': instance.id,
            'neighbor_address': instance.neighbor_address,
            'ownership_info' : ownership_info,
            'power_trace' : None if instance.power_trace == {} else instance.power_trace,
            'owner_status' : instance.owner_status,
            'power_trace_status': instance.power_trace_status,
            'status' : instance.status,
            'property' : instance.property.id,
            'latitude' : instance.latitude,
            'longitude' : instance.longitude,
            'requested_by' : instance.requested_by.id,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        return representation


class PlanSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Plans
        fields = '__all__'

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'plan_name': instance.plan_name,
            'plan_cost': float(instance.plan_cost),
            'plan_coin': float(instance.plan_coin),
            'created_by': instance.created_by.id,
            'updated_by': instance.updated_by.id if instance.updated_by !=None else None,
            'description': instance.description,
            'image': instance.image,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        return representation


class PaymentPlanSerializer(serializers.ModelSerializer) :
    class Meta :
        model = PaymentPlan
        fields = '__all__'

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'payment_plan_name': instance.payment_plan_name,
            'payment_plan_coin': float(instance.payment_plan_coin),
            'plan' : PlanSerializer(Plans.objects.get(id = instance.plan.id)).data,
            'created_by': instance.created_by.id,
            'updated_by': instance.updated_by.id if instance.updated_by !=None else None,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        return representation


class UpgradeProfileSerializer(serializers.ModelSerializer) :
    class Meta :
        model = UpgradeProfile
        fields = '__all__'

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'user': UserSerializer(User.objects.get(id= instance.user.id)).data,
            'coin' : float(instance.coin),
            'plan' : PlanSerializer(Plans.objects.get(id = instance.plan.id)).data,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        return representation


class PaymentTransactionSerializer(serializers.ModelSerializer) :
    class Meta :
        model = PaymentTransaction
        fields = '__all__'

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'property': PropertySerializer(Property.objects.get(id= instance.property.id)).data,
            'payment_plan' : PaymentPlanSerializer(PaymentPlan.objects.get(id = instance.payment_plan.id)).data,
            'transaction_coin' : instance.transaction_coin,
            'created_by' :  UserSerializer(User.objects.get(id=instance.created_by.id)).data,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }
        return representation


class UpgradeHistorySerializer(serializers.ModelSerializer):
    class Meta :
        model = UpgradeHistory
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta :
        model = Notification
        fields = '__all__'

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            # "level": instance.level,
            # "unread": instance.unread,
            "actor_object_id": int(instance.actor_object_id),
            "verb": instance.verb,
            # "description": instance.description,
            # "target_object_id": instance.target_object_id,
            "action_object_object_id": int(instance.action_object_object_id) if instance.action_object_object_id else None,
            "timestamp": instance.timestamp,
            # "public": instance.public,
            # "deleted": instance.deleted,
            # "emailed": instance.emailed,
            # "data": instance.data,
            "recipient": UserSerializer(User.objects.get(id= instance.recipient.id)).data,
            # "actor_content_type": instance.actor_content_type,
            # "target_content_type": instance.target_content_type,
            "action_object_content_type": ContentType.objects.get(id=instance.action_object_content_type.id).model if instance.action_object_content_type else None
        }
        return representation


class MailWizardInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailWizardInfo
        fields = '__all__'


class MailWizardSubsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailWizardSubsType
        fields = '__all__'


class MailWizardUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailWizardUserInfo
        fields = '__all__'


class BillingCardInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingCardInfo
        fields = '__all__'


class PropertyLatLongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = 'id,latitude,longitude'

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "latitude" : instance.latitude,
            "longitude" : instance.longitude
        }
        return representation


class TeamVisitedPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

    def to_representation(self, instance):

        # instance is the model object. create the custom json format by accessing instance
        # attributes normaly and return it
        try:
            user_list_id = instance.user_list.id
        except:
            user_list_id = None
        try:
            history = HistoryDetail.objects.filter(property__id=instance.id)[0].history.id
        except:
            history =None
        representation = {
            'id': instance.id,
            'user': UserSerializer(User.objects.get(id=UserList.objects.get(id=user_list_id).user.id)).data,
            # 'user_list_details': UserListSerializer(UserList.objects.get(id=user_list_id)).data,
            'street': instance.street,
            'city': instance.city,
            'state': instance.state,
            'zip': instance.zip,
            'photo_count' : PropertyPhotos.objects.filter(property=instance).count(),
            'note_count': PropertyNotes.objects.filter(property=instance).count(),
            'history': history,
            'created_at': instance.created_at,
            'updated_at' : instance.updated_at
        }
        return representation


class ClusterViewByListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = 'id,latitude,longitude,property_tags'

    def to_representation(self, instance):
        representation = {
            "id": instance.id,
            "latitude" : instance.latitude,
            "longitude" : instance.longitude,
            'property_tags' : instance.property_tags,
        }
        return representation
