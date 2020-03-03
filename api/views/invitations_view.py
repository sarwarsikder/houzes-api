import decimal
from django.db.models import Q
from django.db.models.expressions import RawSQL, F, ExpressionWrapper
from oauth2_provider.models import AccessToken
# from django.utils import simplejson
from rest_framework import viewsets, status
from rest_framework.decorators import action

from api.serializers import *
from api.models import *
from django.core.mail import send_mail
from rest_framework.response import Response
import shortuuid
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import json
import datetime
from django.core import serializers
from django.db.models import Sum, DurationField, Count, IntegerField
from django.utils.dateparse import parse_duration

from api.views.send_email_view import SendEmailViewSet
import datetime
import pytz


class InvitationsViewSet(viewsets.ModelViewSet):
    queryset = Invitations.objects.all()
    serializer_class = InvitationsSerializer

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):
        try:
            receiver = request.data['email'].lower().strip()
        except:
            receiver = request.body['email'].lower().strip()

        invitation_count = 0
        invitation_count = User.objects.filter(invited_by=request.user.id).count() + Invitations.objects.filter(
            user__id=request.user.id).count()
        if invitation_count > 9:
            status = False
            data = None
            message = "You can't invite more than 10 members"
            return Response({'status': status, 'data': data, 'message': message})

        if User.objects.filter(email=receiver).first():
            status = False
            data = None
            message = 'User already exist'
            return Response({'status': status, 'data': data, 'message': message})

        status = False
        data = None
        message = ""

        invitation_key = generate_shortuuid()

        if Invitations.objects.filter(email=receiver, user__id=request.user.id).first():
            try:
                Invitations.objects.filter(email=receiver, user__id=request.user.id).delete()
                subject = 'Invitation'
                body = str(request.user) + " sent you an invitation click the link below to accept."
                email = receiver
                url = 'https://' + settings.WEB_APP_URL + '/team-invite/' + str(invitation_key)
                SendEmailViewSet.send_email_view(self, subject, body, email, '', url)

                invitations = Invitations(user=User.objects.get(id=request.user.id), invitation_key=invitation_key,
                                          email=receiver, status=0)
                invitations.save()
                invitationsSerializer = InvitationsSerializer(invitations)
                status = True
                data = invitationsSerializer.data
                message = "Invitation resent"
            except:
                status = False
                message = "User is not invited"
            return Response({'status': status, 'data': data, 'message': message})

        try:
            subject = 'Invitation'
            body = str(request.user) + " sent you an invitation. Click the below link to accept."
            email = receiver
            url = 'https://' + settings.WEB_APP_URL + '/team-invite/' + str(invitation_key)
            SendEmailViewSet.send_email_view(self, subject, body, email, 'concern', url)

            invitations = Invitations(user=User.objects.get(id=request.user.id), invitation_key=invitation_key,
                                      email=receiver, status=0)
            invitations.save()
            invitationsSerializer = InvitationsSerializer(invitations)
            status = True
            data = invitationsSerializer.data
            message = "User invited. Pending acceptance"
        except:
            status = False
            message = "User is not invited"
        return Response({'status': status, 'data': data, 'message': message})

    def list(self, request, *args, **kwargs):
        if User.objects.get(id=request.user.id).is_admin:
            users = UserSerializer(User.objects.filter(Q(invited_by=request.user.id) | Q(id=request.user.id)),
                                   many=True)
            unregistered_invitations = InvitationsSerializer(Invitations.objects.filter(user_id=request.user.id),
                                                             many=True)
            dict = {
                'users': users.data,
                'unregistered_invitations': unregistered_invitations.data,
            }
        else:
            user = User.objects.get(id=request.user.id)
            users = UserSerializer(User.objects.filter(Q(invited_by=user.invited_by) | Q(id=user.invited_by)),
                                   many=True)
            unregistered_invitations = InvitationsSerializer(Invitations.objects.filter(user_id=user.invited_by),
                                                             many=True)
            dict = {
                'users': users.data,
                'unregistered_invitations': unregistered_invitations.data
            }

        return JsonResponse(dict)

    def destroy(self, request, *args, **kwargs):
        invitationId = kwargs['pk']
        status = False
        message = ""
        try:
            Invitations.objects.get(id=invitationId).delete()
            status = True
            message = "Invitation deleted successfully"
        except:
            status = False
            message = "Invitation is not deleted"
        return Response({'status': status, 'message': message})

    @action(detail=False, url_path='activity')
    def team_activity(self, request, *args, **kwargs):
        if User.objects.get(id=request.user.id).is_admin:
            users = User.objects.filter(invited_by=request.user.id)
            activities = []
            for user in users:
                userLists = UserList.objects.filter(user=user)
                houzes_count = Property.objects.filter(user_list__in=userLists).count()
                properties = Property.objects.filter(Q(user_list__in=userLists), ~Q(property_tags=[]))
                tagged_houzes_count = properties.count()
                length_count = History.objects.filter(user=user).aggregate(Sum('length'))['length__sum']
                if (length_count == None):
                    length_count = 0

                length_count = length_count * decimal.Decimal(0.621371)
                durations = History.objects.annotate(
                    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())).filter(
                    user=user)
                duration_count = InvitationsViewSet.datetime_parse(durations.aggregate(Sum('diff')))

                productivity = 0
                try:
                    productivity = tagged_houzes_count / duration_count
                except:
                    productivity = 0
                activity = {
                    'user_id': user.id,
                    'user_first_name': user.first_name,
                    'user_last_name': user.last_name,
                    'total_houzes': houzes_count,
                    'total_miles': length_count,
                    'total_duration': duration_count,
                    'total_tagged_houzes': tagged_houzes_count,
                    'productivity': productivity
                }
                activities.append(activity)

            return Response(activities)

    @action(detail=False, url_path='total-houzes/filter')
    def total_houzes_filter(self, request, *args, **kwargs):
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        date_format = '%Y-%m-%d'

        unaware_start_time = datetime.datetime.strptime(start_time, date_format)
        aware_start_time = pytz.utc.localize(unaware_start_time)

        unaware_end_time = datetime.datetime.strptime(end_time, date_format)
        aware_end_time = pytz.utc.localize(unaware_end_time) + datetime.timedelta(days=1)

        print(aware_start_time)
        print(aware_end_time)

        if User.objects.get(id=request.user.id).is_admin:
            users = User.objects.filter(invited_by=request.user.id)
            total_houzes = []
            for user in users:
                userLists = UserList.objects.filter(user=user)
                houzes_count = Property.objects.filter(
                    Q(user_list__in=userLists) & Q(created_at__range=[aware_start_time, aware_end_time])).count()
                total_houze = {
                    'user_id': user.id,
                    'user_first_name': user.first_name,
                    'user_last_name': user.last_name,
                    'total_houzes': houzes_count
                }
                total_houzes.append(total_houze)

            return Response(total_houzes)

    @action(detail=False, url_path='total-miles/filter')
    def total_miles_filter(self, request, *args, **kwargs):
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        date_format = '%Y-%m-%d'

        unaware_start_time = datetime.datetime.strptime(start_time, date_format)
        aware_start_time = pytz.utc.localize(unaware_start_time)

        unaware_end_time = datetime.datetime.strptime(end_time, date_format)
        aware_end_time = pytz.utc.localize(unaware_end_time) + datetime.timedelta(days=1)

        if User.objects.get(id=request.user.id).is_admin:
            users = User.objects.filter(invited_by=request.user.id)
            total_miles = []
            for user in users:
                length_count = \
                    History.objects.filter(
                        Q(user=user) & Q(created_at__range=[aware_start_time, aware_end_time])).aggregate(
                        Sum('length'))['length__sum']
                if (length_count == None):
                    length_count = 0

                length_count = length_count * decimal.Decimal(0.621371)

                total_mile = {
                    'user_id': user.id,
                    'user_first_name': user.first_name,
                    'user_last_name': user.last_name,
                    'user_photo': user.photo,
                    'total_miles': length_count
                }
                total_miles.append(total_mile)

            return Response(total_miles)

    @action(detail=False, url_path='total-duration/filter')
    def total_duration_filter(self, request, *args, **kwargs):
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        print(start_time)
        print(end_time)

        date_format = '%Y-%m-%d'

        unaware_start_time = datetime.datetime.strptime(start_time, date_format)
        aware_start_time = pytz.utc.localize(unaware_start_time)

        unaware_end_time = datetime.datetime.strptime(end_time, date_format)
        aware_end_time = pytz.utc.localize(unaware_end_time) + datetime.timedelta(days=1)

        if User.objects.get(id=request.user.id).is_admin:
            users = User.objects.filter(invited_by=request.user.id)
            total_duration = []
            for user in users:
                durations = History.objects.annotate(
                    diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())).filter(
                    Q(user=user) & Q(created_at__range=[aware_start_time, aware_end_time]))
                duration_count = InvitationsViewSet.datetime_parse(durations.aggregate(Sum('diff')))

                activity = {
                    'user_id': user.id,
                    'user_first_name': user.first_name,
                    'user_last_name': user.last_name,
                    'user_photo': user.photo,
                    'total_duration': duration_count
                }
                total_duration.append(activity)

            return Response(total_duration)

    def datetime_parse(value):
        data = value['diff__sum']
        if data:
            days, seconds = data.days, data.seconds
            hours = days * 24 + seconds / 3600
            return hours
        else:
            return 0

    @action(detail=False, url_path='list')
    def team_list(self, request, *args, **kwargs):
        if User.objects.get(id=request.user.id).is_admin:
            users = UserSerializer(User.objects.filter(invited_by=request.user.id), many=True)
            unregistered_invitations = InvitationsSerializer(Invitations.objects.filter(user_id=request.user.id),
                                                             many=True)
            dict = {
                'users': users.data,
                'unregistered_invitations': unregistered_invitations.data,
            }
        else:
            user = User.objects.get(id=request.user.id)
            users = UserSerializer(User.objects.filter(invited_by=user.invited_by), many=True)
            unregistered_invitations = InvitationsSerializer(Invitations.objects.filter(user_id=user.invited_by),
                                                             many=True)
            team_manager = UserSerializer(User.objects.get(id=user.invited_by))
            dict = {
                'users': users.data,
                'unregistered_invitations': unregistered_invitations.data,
                'team_manager': team_manager.data
            }

        return JsonResponse(dict)
